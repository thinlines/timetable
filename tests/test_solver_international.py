from scheduler.solver import solve
from models.time_periods import create_time_period
from models.facilities import create_facility
from models.teachers import create_teacher
from models.courses import create_course
from models.class_sections import create_class_section
from db import add_student, get_connection
from repository import fetch_scheduled_classes


def test_international_teacher_avoids_first_and_last_periods():
    # Make sure eligibility table doesn't interfere
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "TRUNCATE TABLE teacher_courses RESTART IDENTITY CASCADE;")
    finally:
        conn.close()

    # Create three periods in the same day: 1, 2, 3
    p1 = create_time_period(period_number=1, day_of_week=1)
    p2 = create_time_period(period_number=2, day_of_week=1)
    p3 = create_time_period(period_number=3, day_of_week=1)
    create_facility(name="Room 1")

    # International teacher should only be scheduled in middle period (2)
    teacher = create_teacher(
        name="Intl", max_periods_per_week=1, is_international=True)
    course = create_course(code="I1", name="Intl Course", periods_per_week=1)
    section = create_class_section(
        course_id=course.id, section_name="A", semester="2024")
    add_student("S1", "Student One", 10)

    solve()

    all_classes = fetch_scheduled_classes()

    rows = fetch_scheduled_classes(section_id=section.id)
    assert len(rows) == 1
    # (id, class_section_id, teacher_id, facility_id, time_period_id)
    _, _, teacher_id, _, period_id = rows[0]
    assert teacher_id == teacher.id
    assert period_id == p2.id  # middle period only
