from models.class_sections import (
    create_class_section,
    get_class_section,
    update_class_section,
    delete_class_section,
)
from models.courses import create_course


def test_class_section_crud_cycle():
    course = create_course("SCI101", "Science", 4)
    section = create_class_section(course_id=course.id, section_name="A")
    fetched = get_class_section(section.id)
    assert fetched == section

    updated = update_class_section(section.id, section_name="B", max_students=30)
    assert updated.section_name == "B"
    assert updated.max_students == 30

    assert delete_class_section(section.id) is True
    assert get_class_section(section.id) is None
