# models_router.py
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form, Header, Query

from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import numpy as np
from sklearn.decomposition import PCA

from database import get_db
from models import MLModel
from schemas import MLModelBase

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/", response_model=List[MLModelBase])
def list_models(db: Session = Depends(get_db)):
    return db.query(MLModel).order_by(MLModel.id).all()


@router.post("/{code}/default")
def set_default_model(code: str, db: Session = Depends(get_db)):
    model = db.query(MLModel).filter(MLModel.code == code).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model không tồn tại")

    # reset default
    db.query(MLModel).update({MLModel.is_default: False})

    # set default mới
    model.is_default = True
    db.commit()

    return {"message": f"Đã đặt {code} làm default"}


# === Embed viz (fallback sang v5 nếu thiếu) ===
@router.get("/embed_viz")
def get_embed_viz(model_code: str = Query(...)):
    base_dir = Path(__file__).resolve().parent / "ml" / "models"
    model_dir = base_dir / model_code
    candidates = [
        (model_dir / "gallery_embs.npy", model_dir / "gallery_files.txt"),
        (model_dir / "bottom_embs_v5.npy", model_dir / "bottom_files_v5.txt"),
    ]
    emb_path = files_path = None
    for e, f in candidates:
        if e.exists() and f.exists():
            emb_path, files_path = e, f
            break
    if not emb_path:
        raise HTTPException(status_code=404, detail="missing_embeddings")

    embs = np.load(emb_path)
    with open(files_path, "r", encoding="utf-8") as f:
        files = [x.strip() for x in f if x.strip()]

    n = min(len(embs), len(files))
    if n == 0: return []
    embs, files = embs[:n].astype(np.float32), files[:n]

    n_components = min(3, max(1, n))
    pca = PCA(n_components=n_components)
    coords = pca.fit_transform(embs)

    out = []
    for i, path in enumerate(files):
        x = float(coords[i][0])
        y = float(coords[i][1]) if n_components > 1 else 0.0
        z = float(coords[i][2]) if n_components > 2 else 0.0
        base = Path(path).stem
        out.append({
            "x": x, "y": y, "z": z,
            "base_name": base,
            "top_image_url": f"/static/top/{base}.jpg",
            "tag": "coaster",
        })
    return out
