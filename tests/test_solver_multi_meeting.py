from scheduler.solver import solve
from models.time_periods import create_time_period
from models.facilities import create_facility
from models.teachers import create_teacher
from models.courses import create_course
from models.class_sections import create_class_section
from db import add_student, get_connection
from repository import fetch_scheduled_classes


def test_solver_schedules_multiple_meetings_for_section():
    # Ensure teacher-course mappings don't leak between runs
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE teacher_courses RESTART IDENTITY CASCADE;")
    finally:
        conn.close()

    # Setup: 3 periods, 1 facility, 1 teacher (enough weekly load)
    p1 = create_time_period(period_number=1, day_of_week=1)
    p2 = create_time_period(period_number=2, day_of_week=1)
    p3 = create_time_period(period_number=3, day_of_week=1)
    create_facility(name="Room 1")
    create_teacher(name="T1", max_periods_per_week=3)

    # Course requires two meetings per week
    course = create_course(code="M1", name="Math", periods_per_week=2)
    section = create_class_section(course_id=course.id, section_name="A", semester="2024")

    # Need at least one student so schedule persists
    add_student("S1", "Student One", 10)

    schedule = solve()
    assert len(schedule) == 2

    # Verify two persisted rows for the section in distinct periods
    rows = fetch_scheduled_classes(section_id=section.id)
    assert len(rows) == 2
    # (id, class_section_id, teacher_id, facility_id, time_period_id)
    period_ids = {r[4] for r in rows}
    assert len(period_ids) == 2
