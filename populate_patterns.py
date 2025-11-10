# populate_patterns.py
import csv
from pathlib import Path

from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Pattern

TOP_DIR = Path("static/top")
BOT_DIR = Path("static/bot")
CAPTION_FILE = Path("static/captions.tsv")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    return SessionLocal()


def slug_to_display_name(base_name: str) -> str:
    if "." in base_name:
        base_name = base_name.split(".")[0]
    cleaned = base_name.replace("-", " ").replace("_", " ").strip()
    if not cleaned:
        return base_name
    return cleaned[0].upper() + cleaned[1:]


def build_index():
    """
    mapping[base_name] = {
        "top": top_filename,
        "bot": bot_filename or None
    }
    """
    mapping = {}

    if TOP_DIR.exists():
        for file in TOP_DIR.iterdir():
            if file.is_file() and file.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                base = file.stem  # "0001"
                mapping.setdefault(base, {})["top"] = file.name

    if BOT_DIR.exists():
        for file in BOT_DIR.iterdir():
            if file.is_file() and file.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                base = file.stem
                mapping.setdefault(base, {})["bot"] = file.name

    return mapping


def load_captions():
    """
    Đọc captions.tsv
    Cột 1: tên ảnh (có thể kèm .jpg/.png)
    Các cột còn lại: phần mô tả -> join thành 1 chuỗi.

    Trả về: { base_name (không phần mở rộng) : caption_str }
    """
    captions = {}

    if not CAPTION_FILE.exists():
        print("⚠ Không tìm thấy static/captions.tsv. Bỏ qua caption.")
        return captions

    with open(CAPTION_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")

        for row in reader:
            if not row or not row[0].strip():
                continue

            raw_name = row[0].strip()

            # Bỏ qua dòng header nếu có
            lower = raw_name.lower()
            if lower in ("image", "filename", "file", "name"):
                continue

            # Chuẩn hóa base_name: bỏ đuôi .jpg/.png
            if "." in raw_name:
                base_name = raw_name.rsplit(".", 1)[0]
            else:
                base_name = raw_name

            # Caption = nối các cột còn lại
            if len(row) >= 2:
                parts = [c.strip() for c in row[1:] if c.strip()]
                caption = " ".join(parts)
            else:
                caption = ""

            if base_name and caption:
                captions[base_name] = caption

    print(f"📖 Đã nạp {len(captions)} caption (chuẩn hóa base_name) từ {CAPTION_FILE}")
    return captions


def populate_patterns():
    init_db()
    db = get_session()
    mapping = build_index()
    captions = load_captions()

    if not mapping:
        print("⚠ Không tìm thấy ảnh trong static/top hoặc static/bot.")
        db.close()
        return

    created = 0
    updated = 0
    untouched = 0

    for base_name, files in mapping.items():
        top_file = files.get("top")
        bot_file = files.get("bot")

        if not top_file:
            print(f"[WARN] Bỏ qua '{base_name}' vì không có ảnh TOP.")
            continue

        caption_text = captions.get(base_name)

        # Tìm pattern đã có
        pattern = (
            db.query(Pattern)
            .filter(Pattern.base_name == base_name)
            .first()
        )

        if pattern:
            # cập nhật đường dẫn nếu thiếu
            changed = False
            if not pattern.top_image_path:
                pattern.top_image_path = top_file
                changed = True
            if bot_file and not pattern.bot_image_path:
                pattern.bot_image_path = bot_file
                changed = True

            # cập nhật description nếu đang rỗng và có caption
            if caption_text and (not pattern.description or not pattern.description.strip()):
                pattern.description = caption_text
                updated += 1
                changed = True

            if changed:
                db.add(pattern)
            else:
                untouched += 1

            continue

        # Nếu chưa có -> tạo mới
        p = Pattern(
            base_name=base_name,
            name=slug_to_display_name(base_name),
            type="coaster",
            difficulty=None,
            tags="coaster",
            top_image_path=top_file,
            bot_image_path=bot_file,
            description=caption_text,
        )
        db.add(p)
        created += 1

    db.commit()
    db.close()

    print(
        f"✅ Đã thêm {created} pattern mới, cập nhật {updated} caption,"
        f" giữ nguyên {untouched} pattern đã có."
    )


if __name__ == "__main__":
    populate_patterns()
