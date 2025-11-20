from __future__ import annotations
from database import Base, engine
import models  # noqa: F401  //F401 는 “사용 안 하는 import지만 오류 내지 마라”는 표시


def init_db() -> None:
    """메모: 필요시 직접 테이블 생성할 때 사용 (Alembic 없이)."""
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    init_db()
    print('테이블 생성 완료')
