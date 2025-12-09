# ml/search_engine.py
import io, sys
from pathlib import Path
from typing import List, Optional
import numpy as np
import faiss
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from torchvision.transforms import InterpolationMode
from transformers import CLIPModel, CLIPProcessor

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def load_index(model_dir: Path):
    # ưu tiên cặp chuẩn, fallback sang v5
    candidates = [
        ("gallery_embs.npy", "gallery_files.txt"),
        ("bottom_embs.npy", "bottom_files.txt"),
        ("bottom_embs_v5.npy", "bottom_files_v5.txt"),
    ]
    emb_path = files_path = None
    for e, f in candidates:
        ep, fp = model_dir / e, model_dir / f
        if ep.exists() and fp.exists():
            emb_path, files_path = ep, fp
            break
    if not emb_path or not files_path:
        raise FileNotFoundError(f"Thiếu bottom_embs/bottom_files trong {model_dir}")

    embs = np.load(emb_path).astype("float32")
    with open(files_path, "r", encoding="utf-8") as f:
        files = [l.strip() for l in f if l.strip()]
    n = min(len(embs), len(files))
    if n == 0:
        raise RuntimeError("Empty index")
    embs, files = embs[:n], files[:n]

    faiss.normalize_L2(embs)
    index = faiss.IndexFlatIP(embs.shape[1])
    index.add(embs)
    base_names = [Path(p).stem for p in files]
    return index, base_names

class BaseRetrievalModel:
    def __init__(self, model_dir: Path):
        self.model_dir = Path(model_dir)
        self.index, self.base_names = load_index(self.model_dir)

    def rank(self, q_emb: np.ndarray, top_k: int) -> List[str]:
        q = q_emb.astype("float32")[None, :]
        faiss.normalize_L2(q)
        _, I = self.index.search(q, top_k)
        return [self.base_names[i] for i in I[0]]

# ---------- Model 1 (image-only CLIP) ----------
class CLIPImageModel(nn.Module):
    def __init__(self, model_name="openai/clip-vit-base-patch16"):
        super().__init__()
        self.clip = CLIPModel.from_pretrained(model_name)
        self.logit_scale = nn.Parameter(torch.ones([]) * np.log(1/0.07))
    def forward(self, images: torch.Tensor):
        z = self.clip.get_image_features(pixel_values=images)
        return F.normalize(z, dim=-1)

class Model1Retrieval(BaseRetrievalModel):
    def __init__(self, model_dir: Path):
        super().__init__(model_dir)
        self.img_t = transforms.Compose([
            transforms.Resize((224, 224), interpolation=InterpolationMode.BICUBIC),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.48145466,0.4578275,0.40821073),
                                 std =(0.26862954,0.26130258,0.27577711)),
        ])
        self.model = CLIPImageModel().to(DEVICE)
        self._load_ckpt(); self.model.eval()

    def _load_ckpt(self):
        cands = [
            self.model_dir / "best_R1.pt",
        ] + list(reversed(sorted(self.model_dir.glob("clip_img_epoch*.pt"))))
        ckpt = next((p for p in cands if p.exists()), None)
        if not ckpt:
            raise FileNotFoundError(f"Không tìm thấy checkpoint trong {self.model_dir}")
        state = torch.load(ckpt, map_location=DEVICE)
        ms = state.get("model_state", state)
        self.model.load_state_dict(ms, strict=False)
        print(f"[Model1Retrieval] Loaded checkpoint: {ckpt}")

    @torch.no_grad()
    def _encode_image(self, img: Image.Image) -> np.ndarray:
        x = self.img_t(img.convert("RGB")).unsqueeze(0).to(DEVICE)
        z = self.model(x)[0].cpu().numpy().astype("float32")
        return z

    def search_by_image_bytes(self, img_bytes: bytes, top_k: int):
        img = Image.open(io.BytesIO(img_bytes))
        return self.rank(self._encode_image(img), top_k)

# ---------- Model 2 (TwoTower proxy) ----------
class TwoTowerModel(BaseRetrievalModel):
    def __init__(self, model_dir: Path, ckpt_name="best_R1.pt"):
        super().__init__(model_dir)
        self.clip = CLIPModel.from_pretrained("openai/clip-vit-base-patch16").to(DEVICE)
        self.proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")
        self.clip.eval()
        self.img_t = transforms.Compose([
            transforms.Resize((224,224), interpolation=InterpolationMode.BICUBIC),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.48145466,0.4578275,0.40821073),
                                 std =(0.26862954,0.26130258,0.27577711)),
        ])
        self.alpha = 0.6

    @torch.no_grad()
    def encode_text(self, text: str) -> np.ndarray:
        tok = self.proc(text=[text], return_tensors="pt", padding=True, truncation=True)
        tok = {k: v.to(DEVICE) for k, v in tok.items()}
        z = self.clip.get_text_features(**tok)
        return F.normalize(z, dim=-1)[0].cpu().numpy().astype("float32")

    @torch.no_grad()
    def encode_image(self, img: Image.Image) -> np.ndarray:
        x = self.img_t(img.convert("RGB")).unsqueeze(0).to(DEVICE)
        z = self.clip.get_image_features(pixel_values=x)
        return F.normalize(z, dim=-1)[0].cpu().numpy().astype("float32")

    def fuse(self, zi=None, zt=None, alpha=None):
        if zi is not None and zt is not None:
            a = float(self.alpha if alpha is None else alpha)
            z = a*zi + (1-a)*zt
            z = z/(np.linalg.norm(z)+1e-12)
            return z.astype("float32")
        return (zi or zt).astype("float32")

    def search_by_text(self, text: str, top_k: int):
        return self.rank(self.encode_text(text), top_k)

    def search_by_image_bytes(self, img_bytes: bytes, top_k: int):
        img = Image.open(io.BytesIO(img_bytes))
        return self.rank(self.encode_image(img), top_k)

    def search_by_image_and_text(self, img_bytes: bytes, text: str, top_k: int, alpha: Optional[float]=None):
        img = Image.open(io.BytesIO(img_bytes))
        zi, zt = self.encode_image(img), self.encode_text(text)
        return self.rank(self.fuse(zi, zt, alpha), top_k)

# ---------- Model 3 (ThreeTower proxy) ----------
class ThreeTowerModel(TwoTowerModel):
    def __init__(self, model_dir: Path, ckpt_name="best_R1.pt"):
        super().__init__(model_dir, ckpt_name)
        self.alpha = 0.6  # ảnh-text fuse

# ---------- Model 4 (MAE) ----------
from transformers import ViTMAEConfig, ViTMAEForPreTraining
from torchvision import transforms as T
from torchvision.transforms import InterpolationMode as Interp2

class SpatialStructureEncoder(nn.Module):
    def __init__(self, in_ch, grid=8, sigma=0.5):
        super().__init__()
        self.dw = nn.Conv2d(in_ch, in_ch, 3, padding=1, groups=in_ch)
        self.pool = nn.AdaptiveAvgPool2d((grid,grid))
        g = torch.linspace(-1,1,grid)
        gx, gy = torch.meshgrid(g,g, indexing='xy')
        mask = torch.exp(-(gx**2+gy**2)/(2*sigma**2))
        self.register_buffer("gmask", mask/mask.sum())
    def forward(self, f):
        x = self.dw(f)
        x = self.pool(x)
        return (x*self.gmask).sum((-1,-2))

class PatternTextureEncoder(nn.Module):
    def __init__(self, dim, groups=8):
        super().__init__()
        self.conv = nn.Conv1d(dim, dim, 3, padding=1, groups=groups)
        self.bn = nn.BatchNorm1d(dim)
        self.act = nn.GELU()
    def forward(self, t):
        x = self.conv(t); x = self.bn(x); x = self.act(x)
        return x.mean(-1)

class StructuralEvaluationHead(nn.Module):
    def __init__(self, d_in, d_out=512):
        super().__init__()
        self.p1 = nn.Linear(d_in, d_out)
        self.p2 = nn.Linear(d_in, d_out)
        self.fuse = nn.Linear(d_out*2, d_out)
        self.norm = nn.LayerNorm(d_out)
    def forward(self, s, p):
        a, b = self.p1(s), self.p2(p)
        x = torch.cat([a,b], -1)
        return F.normalize(self.norm(self.fuse(x)), dim=-1)

class CrochetEncoder(nn.Module):
    def __init__(self, img_size=256, patch_size=16, mask_ratio=0.75, embed_dim=512):
        super().__init__()
        cfg = ViTMAEConfig(image_size=img_size, patch_size=patch_size,
                           mask_ratio=mask_ratio, hidden_size=384,
                           num_hidden_layers=12, num_attention_heads=6,
                           intermediate_size=1536)
        self.mae = ViTMAEForPreTraining(cfg)
        self.vit = self.mae.vit
        dim = self.vit.config.hidden_size
        self.spatial = SpatialStructureEncoder(dim, grid=8, sigma=0.5)
        self.pattern = PatternTextureEncoder(dim, groups=8)
        self.head = StructuralEvaluationHead(dim, embed_dim)
    def _forward_tokens(self, x):
        out = self.vit(pixel_values=x, bool_masked_pos=None,
                       output_hidden_states=False, interpolate_pos_encoding=True)
        return out.last_hidden_state
    def forward(self, images):
        x = self._forward_tokens(images)      # (B,1+N,C)
        tokens = x[:,1:,:]
        B,N,C = tokens.shape
        H=W=int(N**0.5)
        fmap = tokens.reshape(B,H,W,C).permute(0,3,1,2).contiguous()
        f_shape = self.spatial(fmap)
        f_pattern = self.pattern(tokens.transpose(1,2))
        return self.head(f_shape, f_pattern)

class MAEModel(BaseRetrievalModel):
    def __init__(self, model_dir: Path, ckpt_name="best_R1.pth"):
        super().__init__(model_dir)
        self.device = DEVICE
        self.img_t = T.Compose([
            T.Resize((256,256), interpolation=Interp2.BICUBIC),
            T.ToTensor(),
            T.Normalize(mean=(0.5,0.5,0.5), std=(0.5,0.5,0.5)),
        ])
        self.encoder = CrochetEncoder().to(self.device)
        ckpt = self.model_dir/ckpt_name
        if not ckpt.exists():
            raise FileNotFoundError(f"Không tìm thấy checkpoint {ckpt}")
        state = torch.load(ckpt, map_location=self.device)
        sd = state.get("state_dict", state)
        self.encoder.load_state_dict(sd, strict=False)
        self.encoder.eval()

    @torch.no_grad()
    def encode_img(self, img: Image.Image) -> np.ndarray:
        x = self.img_t(img.convert("RGB")).unsqueeze(0).to(self.device)
        z = self.encoder(x)[0].cpu().numpy().astype("float32")
        return z

    def search_by_image_bytes(self, img_bytes: bytes, top_k: int):
        img = Image.open(io.BytesIO(img_bytes))
        return self.rank(self.encode_img(img), top_k)

# ---------- Orchestrator ----------
class SearchEngine:
    def __init__(self):
        base = Path(__file__).resolve().parent / "models"
        self.backends = {}
        if (base / "model_1").exists(): self._register("model_1", Model1Retrieval, base/"model_1")
        if (base / "model_2").exists(): self._register("model_2", TwoTowerModel,  base/"model_2")
        if (base / "model_3").exists(): self._register("model_3", ThreeTowerModel,base/"model_3")
        if (base / "model_4").exists(): self._register("model_4", MAEModel,      base/"model_4")
        if not self.backends:
            raise RuntimeError("Không load được model nào. Kiểm tra ml/models/*")

    def _register(self, code, cls, model_dir: Path):
        try:
            self.backends[code] = cls(model_dir)
            print(f"[SearchEngine] Loaded {code} from {model_dir}")
        except Exception as e:
            print(f"[SearchEngine][ERROR] Lỗi khi load {code}: {e}", file=sys.stderr)

    def _get(self, code: str):
        if code not in self.backends:
            raise ValueError(f"Model code không hỗ trợ hoặc chưa load: {code}")
        return self.backends[code]

    def search_by_text(self, model_code: str, query: str, top_k: int):
        be = self._get(model_code)
        if not hasattr(be, "search_by_text"):
            raise ValueError(f"Model {model_code} không hỗ trợ search text")
        return be.search_by_text(query, top_k)

    def search_by_image_bytes(self, model_code: str, img_bytes: bytes, top_k: int):
        be = self._get(model_code)
        if not hasattr(be, "search_by_image_bytes"):
            raise ValueError(f"Model {model_code} không hỗ trợ search image")
        return be.search_by_image_bytes(img_bytes, top_k)

    def search_by_image_and_text(self, model_code: str, img_bytes: bytes, text: str, top_k: int, alpha: Optional[float]=None):
        be = self._get(model_code)
        if not hasattr(be, "search_by_image_and_text"):
            raise ValueError(f"Model {model_code} không hỗ trợ search image+text")
        return be.search_by_image_and_text(img_bytes, text, top_k, alpha)

search_engine = SearchEngine()
