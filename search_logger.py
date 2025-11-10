# backend/search_logger.py (có thể đặt chung trong search_router)
from models import SearchLog
from sqlalchemy.orm import Session
import json

def log_search(db: Session, user_id: int | None, model_code: str, query_text: str | None, image_name: str | None, result_ids: list[int]):
    log = SearchLog(
        user_id=user_id,
        model_code=model_code,
        query_text=query_text,
        image_name=image_name,
        result_ids=json.dumps(result_ids) if result_ids else None,
    )
    db.add(log)
    db.commit()
