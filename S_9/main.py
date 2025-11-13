from __future__ import annotations
from database import Base, engine
import models  # noqa: F401  # 메모: 모델 로딩용 (Alembic 없이 직접 생성할 때만 사용)


def init_db() -> None:
    """메모: 필요시 직접 테이블 생성할 때 사용 (Alembic 없이)."""
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    # 디버깅용 — Alembic 쓰면 굳이 안 써도 됨
    init_db()
    print('테이블 생성 완료')
