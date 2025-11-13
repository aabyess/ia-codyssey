# 메모: SQLite + SQLAlchemy 세팅 (세션/엔진/베이스 정의)

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite 데이터베이스 URL
SQLALCHEMY_DATABASE_URL = 'sqlite:///./mars.db' # DB 접속 주소(URL) 형식

# DB랑 실제로 연결해주는 애 (연결 파이프)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, #아까 말한 SQLite 파일 경로
    connect_args={'check_same_thread': False},
    # SQLite 기본 설정은
    # “이 연결(커넥션)을 만든 쓰레드에서만 써라” 라는 제한
    # 근데 웹 서버(FastAPI, Uvicorn)는 요청마다 다른 쓰레드를 쓸 수 있음
    # 그래서 이 제한을 풀어줘야 함 → False 로 꺼버림
)

# DB에 쿼리 날릴 때 쓰는 “세션 공장”
SessionLocal = sessionmaker( # 세션을 만들어주는 공장 함수
    autocommit=False, #자동으로 커밋하지 마라는 뜻.
    autoflush=False, #자동으로 플러시하지 마라는 뜻.
    bind=engine, #위에서 만든 엔진(연결 파이프)랑 연결
)

# 모든 ORM 모델이 상속받는 부모 클래스
Base = declarative_base()