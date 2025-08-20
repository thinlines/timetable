import os
import sys
import pytest
from db import init_db, get_connection

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture(autouse=True)
def db_env(monkeypatch):
    monkeypatch.setenv("POSTGRES_DB", "postgres")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "postgres")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    init_db()
    # clean table between tests (adjust table name if needed)
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE students RESTART IDENTITY CASCADE;")
    finally:
        conn.close()
