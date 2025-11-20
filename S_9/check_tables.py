from database import engine

with engine.connect() as conn:
    rows = conn.exec_driver_sql(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall() #SQL 실행 결과를 “모든 행”으로 가져오는 함수.
    print(rows)
