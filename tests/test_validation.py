import pytest
from timetable_ortools import solve_timetable, validate_config, DAYS, PERIODS


def test_solve_simple_valid():
    config = {
        "teachers": [{"id": 1, "name": "Teacher"}],
        "courses": [{"id": 1, "name": "Math", "teacher_id": 1}],
        "classes": {"ClassA": {"courses": [{"course_id": 1, "periods_per_week": 4}]}},
        "teacher_limits": {1: 10},
    }

    timetable = solve_timetable(config)
    periods = [v for v in timetable["ClassA"].values() if v is not None]
    assert len(periods) == 4


def test_validate_config_class_overflow():
    too_many = len(DAYS) * len(PERIODS) + 1
    config = {
        "teachers": [{"id": 1, "name": "Teacher"}],
        "courses": [{"id": 1, "name": "Math", "teacher_id": 1}],
        "classes": {"ClassA": {"courses": [{"course_id": 1, "periods_per_week": too_many}]}},
        "teacher_limits": {1: too_many},
    }

    with pytest.raises(ValueError):
        validate_config(config)
