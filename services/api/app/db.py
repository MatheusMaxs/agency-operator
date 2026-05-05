from pathlib import Path
from typing import Iterator

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.settings import settings


pool: ConnectionPool | None = None


def init_pool() -> None:
    global pool
    if pool is None:
        pool = ConnectionPool(
            conninfo=settings.database_url,
            kwargs={"row_factory": dict_row},
            min_size=1,
            max_size=10,
            open=True,
        )


def get_conn() -> Iterator:
    if pool is None:
        init_pool()
    assert pool is not None
    return pool.connection()


def init_db() -> None:
    init_pool()
    schema_path = Path("/app/packages/database/schema.sql")
    schema_sql = schema_path.read_text(encoding="utf-8")
    with get_conn() as conn:
        conn.execute(schema_sql)
