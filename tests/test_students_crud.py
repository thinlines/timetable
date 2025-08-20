from db import (
    add_student,
    delete_student,
    get_connection,
    get_student,
    update_student,
)


def test_get_student_fetches_row():
    add_student("S1", "Alice", 10)
    fetched = get_student("S1")
    assert fetched[1:] == ("S1", "Alice", 10)


def test_update_student_modifies_row():
    add_student("S1", "Alice", 10)
    updated = update_student("S1", name="Alicia", grade_level=11)
    assert updated[1:] == ("S1", "Alicia", 11)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT student_id, name, grade_level FROM students WHERE student_id=%s",
                ("S1",),
            )
            assert cur.fetchone() == ("S1", "Alicia", 11)
    finally:
        conn.close()


def test_delete_student_removes_row():
    add_student("S1", "Alice", 10)
    assert delete_student("S1") is True

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM students WHERE student_id=%s",
                ("S1",),
            )
            assert cur.fetchone() is None
    finally:
        conn.close()

