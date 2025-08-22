from __future__ import annotations

from typing import List, Tuple

from db import get_connection

Assignment = Tuple[int, int, int, int]


def fetch_class_sections() -> List[Tuple[int]]:
    """Return all class section IDs."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM class_sections")
            return cur.fetchall()
    finally:
        conn.close()


def fetch_teachers() -> List[Tuple[int, int, str | None]]:
    """Return all teachers with max load and preferred periods."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, max_periods_per_week, preferred_periods FROM teachers"
            )
            return cur.fetchall()
    finally:
        conn.close()


def fetch_facilities() -> List[Tuple[int]]:
    """Return all facility IDs."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM facilities")
            return cur.fetchall()
    finally:
        conn.close()


def fetch_periods() -> List[Tuple[int]]:
    """Return all time period IDs."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM time_periods")
            return cur.fetchall()
    finally:
        conn.close()


def fetch_student_ids() -> List[int]:
    """Return all student IDs."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM students")
            rows = cur.fetchall()
            return [r[0] for r in rows]
    finally:
        conn.close()


def insert_scheduled_class(
    cur, class_section_id: int, teacher_id: int, facility_id: int, period_id: int
) -> int:
    """Insert a scheduled class and return its ID."""
    cur.execute(
        "SELECT semester FROM class_sections WHERE id=%s", (class_section_id,)
    )
    semester = cur.fetchone()[0]
    cur.execute(
        """
        INSERT INTO scheduled_classes
            (class_section_id, teacher_id, facility_id, time_period_id, semester)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (class_section_id, teacher_id, facility_id, period_id, semester),
    )
    return cur.fetchone()[0]


def bulk_enroll_students(
    cur, scheduled_class_id: int, student_ids: List[int]
) -> None:
    """Enroll multiple students into ``scheduled_class_id``."""
    if not student_ids:
        return
    cur.executemany(
        "INSERT INTO class_enrollments (scheduled_class_id, student_id) VALUES (%s, %s)",
        [(scheduled_class_id, sid) for sid in student_ids],
    )


def persist_schedule(assignments: List[Assignment]) -> None:
    """Persist schedule into ``scheduled_classes`` and ``class_enrollments``."""
    if not assignments:
        return

    student_ids = fetch_student_ids()
    if not student_ids:
        return

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                for class_id, teacher_id, facility_id, period_id in assignments:
                    scheduled_id = insert_scheduled_class(
                        cur, class_id, teacher_id, facility_id, period_id
                    )
                    bulk_enroll_students(cur, scheduled_id, student_ids)
    finally:
        conn.close()
