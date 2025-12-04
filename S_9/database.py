from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

# SQLite DB 파일 이름
SQLALCHEMY_DATABASE_URL = "sqlite:///./mars.db"

# SQLite 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 세션팩토리
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ORM 모델이 상속받는 Base 클래스
Base = declarative_base()


# 🔥 과제 핵심: contextlib 기반 get_db()
@contextmanager
def get_db():
    """
    메모: DB 연결 후 자동 종료하는 contextmanager 기반 의존성 주입 함수
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI에서는 Depends()로 사용하기 위해 래퍼 필요
def get_db_dep():
    with get_db() as db:
        yield db
