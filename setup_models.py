# setup_models.py
from database import SessionLocal, engine
from models import MLModel  # Base là declarative_base() chứa MLModel
from database import Base
def main():
    # 1) Tạo bảng nếu chưa có
    Base.metadata.create_all(bind=engine)

    # 2) Seed / cập nhật models
    seed = [
        dict(code="model_1", name="CLIP Image-only",
             description="Chỉ hỗ trợ tìm theo ảnh",
             top_k=20,  is_default=False),
        dict(code="model_2", name="CLIP TwoTower",
             description="Ảnh + Text (two-tower CLIP)", top_k=20,
              is_default=False),
        dict(code="model_3", name="CLIP ThreeTower",
             description="Three-tower demo", top_k=20,
              is_default=False),
        dict(code="model_4", name="MAE Retrieval v1",
             description="Encoder MAE đã finetune cho coaster", top_k=20,
             is_default=True),
    ]

    with SessionLocal() as session:
        for m in seed:
            row = session.query(MLModel).filter_by(code=m["code"]).first()
            if row:
                # update nhẹ
                row.name = m["name"]
                row.description = m["description"]
                row.top_k = m["top_k"]
                row.embedding_dim = m["embedding_dim"]
                row.is_default = m["is_default"]
            else:
                row = MLModel(**m)
                session.add(row)
        session.commit()

if __name__ == "__main__":
    main()
