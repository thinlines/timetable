from dataclasses import dataclass
from datetime import time
from typing import Optional

from db import get_connection


@dataclass
class TimePeriod:
    id: Optional[int]
    period_number: int
    day_of_week: Optional[int] = None
    period_type: str = "regular"
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_active: bool = True
    special_notes: Optional[str] = None


def create_time_period(
    period_number: int,
    day_of_week: Optional[int] = None,
    period_type: str = "regular",
    start_time: Optional[time] = None,
    end_time: Optional[time] = None,
    is_active: bool = True,
    special_notes: Optional[str] = None,
) -> TimePeriod:
    sql = """
        INSERT INTO time_periods (period_number, day_of_week, period_type,
                                  start_time, end_time, is_active, special_notes)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        RETURNING id, period_number, day_of_week, period_type,
                  start_time, end_time, is_active, special_notes;
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        period_number,
                        day_of_week,
                        period_type,
                        start_time,
                        end_time,
                        is_active,
                        special_notes,
                    ),
                )
                row = cur.fetchone()
                return TimePeriod(*row)
    finally:
        conn.close()


def get_time_period(tp_id: int) -> Optional[TimePeriod]:
    sql = """
        SELECT id, period_number, day_of_week, period_type,
               start_time, end_time, is_active, special_notes
        FROM time_periods WHERE id=%s
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (tp_id,))
            row = cur.fetchone()
            return TimePeriod(*row) if row else None
    finally:
        conn.close()


def update_time_period(tp_id: int, **fields) -> TimePeriod:
    if not fields:
        raise ValueError("No fields to update")
    cols = []
    vals = []
    for k, v in fields.items():
        cols.append(f"{k}=%s")
        vals.append(v)
    vals.append(tp_id)
    sql = f"""
        UPDATE time_periods SET {', '.join(cols)} WHERE id=%s
        RETURNING id, period_number, day_of_week, period_type,
                  start_time, end_time, is_active, special_notes
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(vals))
                row = cur.fetchone()
                return TimePeriod(*row)
    finally:
        conn.close()


def delete_time_period(tp_id: int) -> bool:
    sql = "DELETE FROM time_periods WHERE id=%s"
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, (tp_id,))
                return cur.rowcount > 0
    finally:
        conn.close()
