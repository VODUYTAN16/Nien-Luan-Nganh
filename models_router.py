# models_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

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
