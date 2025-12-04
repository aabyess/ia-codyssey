# main.py

from fastapi import FastAPI

from database import Base, engine
import models  # noqa: F401  # 모델 불러오기
from fastapi.middleware.cors import CORSMiddleware
from domain.question.question_router import router as question_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 모든 출처 허용 (개발용)
    allow_credentials=True,
    allow_methods=["*"],          # 모든 HTTP 메소드 허용
    allow_headers=["*"],          # 모든 헤더 허용
)


# 라우터 등록
app.include_router(question_router)


@app.get("/")
def root():
    return {"message": "Mars Q&A API Running"}
