from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Pattern, MLModel
from schemas import SearchResponse, SearchResultItem
from ml.search_engine import search_engine

from search_logger import log_search
from auth_utils import decode_token
from fastapi import Header
router = APIRouter(prefix="/search", tags=["search"])


def pattern_to_result_item(p: Pattern) -> SearchResultItem:
    return SearchResultItem(
        id=p.id,
        base_name=p.base_name,
        name=p.name,
        top_image_url=f"/static/top/{p.top_image_path}",
        difficulty=p.difficulty,
        tags=p.tags,
    )


from search_logger import log_search
from auth_utils import decode_token
from fastapi import Header

@router.post("/", response_model=SearchResponse)
async def search_patterns(
    model_code: str = Form(...),
    query_text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    # decode user_id nếu có
    user_id = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        user_id = decode_token(token)

    model = db.query(MLModel).filter(MLModel.code == model_code).first()
    if not model:
        raise HTTPException(status_code=400, detail="Model không hợp lệ")

    if not query_text and not image:
        raise HTTPException(status_code=400, detail="Thiếu query_text hoặc image")

    if image is not None:
        img_bytes = await image.read()
        base_names = search_engine.search_by_image_bytes(model.code, img_bytes, model.top_k)
    else:
        base_names = search_engine.search_by_text(model.code, query_text or "", model.top_k)

    patterns = db.query(Pattern).filter(Pattern.base_name.in_(base_names)).all()
    base_to_pattern = {p.base_name: p for p in patterns}
    ordered = [pattern_to_result_item(base_to_pattern[b]) for b in base_names if b in base_to_pattern]

    # ✅ Ghi log
    result_ids = [p.id for p in ordered]
    log_search(db, user_id, model_code, query_text, image.filename if image else None, result_ids)

    return SearchResponse(items=ordered)
