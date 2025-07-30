import pytest

from timetable_ortools import DAYS, PERIODS, solve_timetable, validate_config


def base_config():
    """Return a minimal valid configuration for tests."""
    return {
        "teachers": [{"id": 1, "name": "Teacher"}],
        "courses": [{"id": 1, "name": "Math", "teacher_id": 1}],
        "classes": {"ClassA": {"courses": [{"course_id": 1, "periods_per_week": 4}]}},
        "teacher_limits": {1: 10},
    }


def test_solve_simple_valid():
    config = base_config()

    timetable = solve_timetable(config)
    periods = [v for v in timetable["ClassA"].values() if v is not None]
    assert len(periods) == 4


def test_validate_config_class_overflow():
    too_many = len(DAYS) * len(PERIODS) + 1
    config = base_config()
    config["classes"]["ClassA"]["courses"][0]["periods_per_week"] = too_many
    config["teacher_limits"][1] = too_many

    with pytest.raises(ValueError):
        validate_config(config)
