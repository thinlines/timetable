from __future__ import annotations

from typing import Dict, List, Set, Tuple, Optional

from db import get_connection

Assignment = Tuple[int, int, int, int]


def fetch_class_sections() -> List[Tuple[int, int, int]]:
    """
    Return class sections with their required meetings and course linkage.

    Shape: (section_id, periods_per_week, course_id)
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT cs.id, c.periods_per_week, cs.course_id
                FROM class_sections cs
                JOIN courses c ON c.id = cs.course_id
                """
            )
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


def fetch_periods() -> List[Tuple[int, int, int]]:
    """Return all time periods as (id, period_number, day_of_week)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, period_number, day_of_week FROM time_periods")
            return cur.fetchall()
    finally:
        conn.close()


def fetch_teacher_course_map() -> Dict[int, Set[int]]:
    """Return mapping of course_id -> set of eligible teacher_ids.

    If the table is empty, callers may choose to treat all teachers as eligible.
    """
    conn = get_connection()
    mapping: Dict[int, Set[int]] = {}
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT teacher_id, course_id FROM teacher_courses")
            for teacher_id, course_id in cur.fetchall():
                if course_id not in mapping:
                    mapping[course_id] = set()
                mapping[course_id].add(teacher_id)
    finally:
        conn.close()
    return mapping


def fetch_international_teacher_ids() -> Set[int]:
    """Return the set of teacher IDs marked as international."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM teachers WHERE is_international = TRUE")
            return {row[0] for row in cur.fetchall()}
    finally:
        conn.close()


def fetch_courses_require_consecutive() -> Set[int]:
    """Return the set of course IDs that prefer consecutive periods.

    Courses with ``requires_consecutive_periods = TRUE`` will be included.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM courses WHERE requires_consecutive_periods = TRUE"
            )
            return {row[0] for row in cur.fetchall()}
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
                # Insert classes and enroll students, tracking created rows per section
                created_by_section: Dict[int, List[Tuple[int, int]]] = {}
                for class_id, teacher_id, facility_id, period_id in assignments:
                    scheduled_id = insert_scheduled_class(
                        cur, class_id, teacher_id, facility_id, period_id
                    )
                    bulk_enroll_students(cur, scheduled_id, student_ids)
                    created_by_section.setdefault(class_id, []).append(
                        (scheduled_id, period_id)
                    )

                # Map time_period_id -> (day_of_week, period_number)
                cur.execute(
                    "SELECT id, day_of_week, period_number FROM time_periods"
                )
                pmap: Dict[int, Tuple[int, int]] = {
                    pid: (day, pno) for (pid, day, pno) in cur.fetchall()
                }

                # For each section, mark scheduled rows that are part of a same-day
                # consecutive double-period pair
                for section_id, items in created_by_section.items():
                    # Group by day
                    by_day: Dict[int, List[Tuple[int, int, int]]] = {}
                    for sched_id, pid in items:
                        day, pno = pmap[pid]
                        by_day.setdefault(day, []).append((pno, pid, sched_id))

                    to_mark: Set[int] = set()
                    for day, arr in by_day.items():
                        arr.sort()  # sort by period_number
                        for i in range(len(arr) - 1):
                            pno_a, pid_a, sid_a = arr[i]
                            pno_b, pid_b, sid_b = arr[i + 1]
                            if pno_b == pno_a + 1:
                                to_mark.add(sid_a)
                                to_mark.add(sid_b)

                    # Update marked rows
                    for sid in to_mark:
                        cur.execute(
                            "UPDATE scheduled_classes SET is_double_period=TRUE WHERE id=%s",
                            (sid,),
                        )
    finally:
        conn.close()


def fetch_scheduled_classes(
    section_id: Optional[int] = None,
) -> List[Tuple[int, int, int, int, int]]:
    """
    Return scheduled classes.

    Shape per row: (id, class_section_id, teacher_id, facility_id, time_period_id)
    Optionally filter by class_section_id.
    """
    sql = (
        "SELECT id, class_section_id, teacher_id, facility_id, time_period_id "
        "FROM scheduled_classes"
    )
    params: Tuple = ()
    if section_id is not None:
        sql += " WHERE class_section_id=%s"
        params = (section_id,)
    sql += " ORDER BY class_section_id, time_period_id, id"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()
