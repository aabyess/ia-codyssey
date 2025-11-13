from database import engine

with engine.connect() as conn:
    rows = conn.exec_driver_sql(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()
    print(rows)
