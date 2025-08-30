from scheduler.solver import solve
from models.time_periods import create_time_period
from models.facilities import create_facility
from models.teachers import create_teacher
from models.courses import create_course
from models.class_sections import create_class_section
from db import add_student, get_connection
from repository import fetch_scheduled_classes


def test_solver_respects_teacher_course_eligibility():
    # Clean any prior eligibility data
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE teacher_courses RESTART IDENTITY CASCADE;")
    finally:
        conn.close()

    # Setup: 2 periods, 1 facility, 2 teachers
    create_time_period(period_number=1, day_of_week=1)
    create_time_period(period_number=2, day_of_week=1)
    create_facility(name="Room 1")
    t_allowed = create_teacher(name="Allowed", max_periods_per_week=1)
    t_blocked = create_teacher(name="Blocked", max_periods_per_week=1)

    # Course with one meeting
    course = create_course(code="E1", name="Eligible Course", periods_per_week=1)
    section = create_class_section(course_id=course.id, section_name="A", semester="2024")

    # Restrict eligibility to t_allowed only
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO teacher_courses (teacher_id, course_id) VALUES (%s,%s)",
                    (t_allowed.id, course.id),
                )
    finally:
        conn.close()

    # Ensure persistence occurs
    add_student("S1", "Student One", 10)

    solve()

    # Verify scheduled teacher is the allowed one
    rows = fetch_scheduled_classes(section_id=section.id)
    assert len(rows) == 1
    # (id, class_section_id, teacher_id, facility_id, time_period_id)
    assert rows[0][2] == t_allowed.id
