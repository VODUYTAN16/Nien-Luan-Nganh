# search_router.py
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form, Header, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
from pathlib import Path
import numpy as np
from sklearn.decomposition import PCA

from database import get_db
from models import Pattern, MLModel
from schemas import SearchResponse, SearchResultItem
from ml.search_engine import search_engine
from search_logger import log_search
from auth_utils import decode_token

router = APIRouter(prefix="/search", tags=["search"])

# -------- helpers ----------
def pattern_to_result_item(p: Pattern) -> SearchResultItem:
    return SearchResultItem(
        id=p.id,
        base_name=p.base_name,
        name=p.name,
        top_image_url=f"/static/top/{p.top_image_path}",
        difficulty=p.difficulty,
        tags=p.tags,
        description=p.description,
    )

def order_and_serialize(db: Session, base_names: List[str]) -> List[SearchResultItem]:
    if not base_names:
        return []
    rows = db.query(Pattern).filter(Pattern.base_name.in_(base_names)).all()
    mp = {p.base_name: p for p in rows}
    ordered = [pattern_to_result_item(mp[b]) for b in base_names if b in mp]
    return ordered

def get_user_id_from_auth(authorization: Optional[str]) -> Optional[int]:
    if authorization and authorization.startswith("Bearer "):
        return decode_token(authorization.split(" ", 1)[1])
    return None

def ensure_model(db: Session, model_code: str) -> MLModel:
    model = db.query(MLModel).filter(MLModel.code == model_code).first()
    if not model:
        raise HTTPException(status_code=400, detail="Model không hợp lệ")
    return model

# -------- Schemas --------
class TextSearchIn(BaseModel):
    model_code: str
    text: str

# -------- endpoints --------
@router.post("/image")
async def search_by_image(
    model_code: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    user_id = get_user_id_from_auth(authorization)
    model = ensure_model(db, model_code)

    img_bytes = await image.read()

    try:
        base_names = search_engine.search_by_image_bytes(model.code, img_bytes, model.top_k)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    items = order_and_serialize(db, base_names)

    log_search(
        db,
        user_id,
        model_code,
        None,
        image.filename if image else None,
        [x.id for x in items],
    )

    # Trả về mảng bình thường
    return items


@router.post("/text")
async def search_by_text(
    payload: TextSearchIn,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    user_id = get_user_id_from_auth(authorization)

    model = ensure_model(db, payload.model_code)
    text = (payload.text or "").strip()

    if not text:
        raise HTTPException(status_code=400, detail="Thiếu text")

    try:
        base_names = search_engine.search_by_text(model.code, text, model.top_k)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    items = order_and_serialize(db, base_names)

    log_search(db, user_id, payload.model_code, text, None, [x.id for x in items])

    return items      # ← MẢNG BÌNH THƯỜNG


@router.post("/fuse")
async def search_by_image_and_text(
    model_code: str = Form(...),
    text: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    user_id = get_user_id_from_auth(authorization)
    model = ensure_model(db, model_code)

    t = (text or "").strip()
    if not t:
        raise HTTPException(status_code=400, detail="Thiếu text")

    img_bytes = await image.read()

    try:
        base_names = search_engine.search_by_image_and_text(
            model.code, img_bytes, t, model.top_k
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    items = order_and_serialize(db, base_names)

    log_search(
        db,
        user_id,
        model_code,
        t,
        image.filename if image else None,
        [x.id for x in items],
    )

    return items      # ← MẢNG BÌNH THƯỜNG


@router.post("/")
async def search_patterns_compatible(
    model_code: str = Form(...),
    query_text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    user_id = get_user_id_from_auth(authorization)

    model = ensure_model(db, model_code)

    has_text = bool(query_text and query_text.strip())
    has_image = image is not None

    if not has_text and not has_image:
        raise HTTPException(status_code=400, detail="Thiếu query_text hoặc image")

    try:
        if has_text and has_image:
            img_bytes = await image.read()
            base_names = search_engine.search_by_image_and_text(
                model.code, img_bytes, query_text.strip(), model.top_k
            )
        elif has_image:
            img_bytes = await image.read()
            base_names = search_engine.search_by_image_bytes(
                model.code, img_bytes, model.top_k
            )
        else:
            base_names = search_engine.search_by_text(
                model.code, query_text.strip(), model.top_k
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    items = order_and_serialize(db, base_names)

    log_search(
        db,
        user_id,
        model_code,
        query_text.strip() if has_text else None,
        image.filename if has_image else None,
        [x.id for x in items],
    )

    return items      # ← MẢNG BÌNH THƯỜNG