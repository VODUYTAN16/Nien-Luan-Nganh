# patterns_router.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Pattern
from schemas import PatternBase

router = APIRouter(prefix="/patterns", tags=["patterns"])


def build_pattern_response(p: Pattern) -> PatternBase:
    top_url = f"/static/top/{p.top_image_path}" if p.top_image_path else ""
    bot_url = f"/static/bot/{p.bot_image_path}" if p.bot_image_path else None
    return PatternBase(
        id=p.id,
        base_name=p.base_name,
        name=p.name,
        type=p.type,
        difficulty=p.difficulty,
        tags=p.tags,
        top_image_url=top_url,
        bot_image_url=bot_url,
        description=p.description,
    )


@router.get("/", response_model=List[PatternBase])
def list_patterns(
    db: Session = Depends(get_db),
    type: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
):
    query = db.query(Pattern)
    if type:
        query = query.filter(Pattern.type == type)
    if difficulty:
        query = query.filter(Pattern.difficulty == difficulty)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Pattern.name.like(like)) | (Pattern.tags.like(like))
        )
    patterns = query.order_by(Pattern.id).all()
    return [build_pattern_response(p) for p in patterns]


@router.get("/{pattern_id}", response_model=PatternBase)
def get_pattern(pattern_id: int, db: Session = Depends(get_db)):
    p = db.query(Pattern).filter(Pattern.id == pattern_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Không tìm thấy pattern")
    return build_pattern_response(p)
