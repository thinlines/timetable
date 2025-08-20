from db import get_students, get_connection

def test_get_students_reads_inserted_rows():
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO students (student_id, name, grade_level) VALUES (%s,%s,%s)",
                    ("S1", "Alice", 10),
                )
        rows = get_students()
        assert any(r[1:] == ("S1", "Alice", 10) for r in rows)
    finally:
        conn.close()
