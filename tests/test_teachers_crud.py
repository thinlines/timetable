from models.teachers import (
    create_teacher,
    get_teacher,
    update_teacher,
    delete_teacher,
)


def test_teacher_crud_cycle():
    teacher = create_teacher("Alice")
    fetched = get_teacher(teacher.id)
    assert fetched == teacher

    updated = update_teacher(teacher.id, name="Alicia", max_periods_per_week=20)
    assert updated.name == "Alicia"
    assert updated.max_periods_per_week == 20

    assert delete_teacher(teacher.id) is True
    assert get_teacher(teacher.id) is None
