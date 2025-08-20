import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from db import init_db, get_students, get_connection


def test_init_and_display():
    os.environ.setdefault("POSTGRES_DB", "postgres")
    os.environ.setdefault("POSTGRES_USER", "postgres")
    os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
    os.environ.setdefault("POSTGRES_HOST", "localhost")
    os.environ.setdefault("POSTGRES_PORT", "5432")

    init_db()

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO students (student_id, name, grade_level) VALUES (%s, %s, %s)",
            ("S1", "Alice", 10),
        )
    conn.close()

    rows = get_students()
    assert any(r[1] == "S1" and r[2] == "Alice" and r[3] == 10 for r in rows)
