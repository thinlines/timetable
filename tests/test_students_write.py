from db import add_student, get_connection

def test_add_student_inserts_and_returns_row():
    created = add_student("S1", "Alice", 10)
    assert created[1:] == ("S1", "Alice", 10)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT student_id, name, grade_level FROM students WHERE student_id=%s", ("S1",))
            assert cur.fetchone() == ("S1", "Alice", 10)
    finally:
        conn.close()
