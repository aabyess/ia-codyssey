from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# -------------------------------
# ★ 여기 추가해야 하는 부분 ★
#   우리의 Base(metadata)를 불러오기 위해 필요
# -------------------------------
import database
import models  # noqa: F401  # 자동으로 테이블 로딩되게(삭제 금지)

# -------------------------------
# Alembic 기본 설정
# -------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------
# ★ 핵심: Alembic이 참조할 metadata 설정
# -------------------------------
target_metadata = database.Base.metadata
# 기존에 있던 target_metadata = None 은 삭제 또는 덮어쓰기
# -------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
