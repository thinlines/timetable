from datetime import time

from models.time_periods import (
    create_time_period,
    get_time_period,
    update_time_period,
    delete_time_period,
)


def test_time_period_crud_cycle():
    tp = create_time_period(1, day_of_week=1, start_time=time(8, 0), end_time=time(8, 45))
    fetched = get_time_period(tp.id)
    assert fetched == tp

    updated = update_time_period(tp.id, period_number=2)
    assert updated.period_number == 2

    assert delete_time_period(tp.id) is True
    assert get_time_period(tp.id) is None
