from scheduler.solver import solve
from models.courses import create_course
from models.class_sections import create_class_section
from models.teachers import create_teacher
from models.facilities import create_facility
from models.time_periods import create_time_period
from db import add_student, get_connection


def test_solver_returns_feasible_timetable():
    period1 = create_time_period(period_number=1, day_of_week=1)
    period2 = create_time_period(period_number=2, day_of_week=1)
    teacher1 = create_teacher(
        name="T1", max_periods_per_week=1, preferred_periods={"preferred": [period1.id]}
    )
    teacher2 = create_teacher(
        name="T2", max_periods_per_week=1, preferred_periods={"preferred": [period2.id]}
    )
    facility = create_facility(name="Room 1")
    course1 = create_course(code="M1", name="Math", periods_per_week=1)
    course2 = create_course(code="E1", name="Eng", periods_per_week=1)
    section1 = create_class_section(course_id=course1.id, section_name="A", semester="2024")
    section2 = create_class_section(course_id=course2.id, section_name="B", semester="2024")
    add_student("S1", "Student One", 10)

    schedule = solve()
    assert len(schedule) == 2

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT class_section_id, teacher_id, facility_id, time_period_id FROM scheduled_classes ORDER BY class_section_id"
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    assert len(rows) == 2
    # teachers assigned to their preferred periods
    assignment_map = {row[0]: row for row in rows}
    assert assignment_map[section1.id][1] == teacher1.id
    assert assignment_map[section1.id][3] == period1.id
    assert assignment_map[section2.id][1] == teacher2.id
    assert assignment_map[section2.id][3] == period2.id

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM class_enrollments")
            enroll_count = cur.fetchone()[0]
    finally:
        conn.close()

    assert enroll_count == 2  # two scheduled classes with one student each
