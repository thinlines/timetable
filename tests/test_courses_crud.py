from models.courses import (
    create_course,
    get_course,
    update_course,
    delete_course,
)


def test_course_crud_cycle():
    course = create_course("MATH101", "Mathematics", 5)
    fetched = get_course(course.id)
    assert fetched == course

    updated = update_course(course.id, name="Advanced Math")
    assert updated.name == "Advanced Math"

    assert delete_course(course.id) is True
    assert get_course(course.id) is None
