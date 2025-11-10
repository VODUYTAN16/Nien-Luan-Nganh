# main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import Base, engine
from auth_router import router as auth_router
from patterns_router import router as patterns_router
from models_router import router as models_router
from search_router import router as search_router
from populate_patterns import populate_patterns

# Tạo bảng nếu chưa có
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Crochet Coaster API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # chỉnh thành origin của frontend nếu muốn
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static/top", StaticFiles(directory="static/top"), name="static_top")
app.mount("/static/bot", StaticFiles(directory="static/bot"), name="static_bot")

app.include_router(auth_router)
app.include_router(patterns_router)
app.include_router(models_router)
app.include_router(search_router)


@app.on_event("startup")
def on_startup():
    # Tự scan static/top & static/bot, thêm record mới vào patterns (idempotent)
    populate_patterns()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
