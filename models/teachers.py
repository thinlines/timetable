from dataclasses import dataclass
from typing import Optional, Dict, Any
from psycopg2.extras import Json

from db import get_connection


@dataclass
class Teacher:
    id: Optional[int]
    name: str
    employee_id: Optional[str] = None
    max_periods_per_week: int = 24
    is_international: bool = False
    can_supervise_study_hours: bool = True
    departments: Optional[Dict[str, Any]] = None
    preferred_periods: Optional[Dict[str, Any]] = None
    unavailable_periods: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


def create_teacher(
    name: str,
    employee_id: Optional[str] = None,
    max_periods_per_week: int = 24,
    is_international: bool = False,
    can_supervise_study_hours: bool = True,
    departments: Optional[Dict[str, Any]] = None,
    preferred_periods: Optional[Dict[str, Any]] = None,
    unavailable_periods: Optional[Dict[str, Any]] = None,
    notes: Optional[str] = None,
) -> Teacher:
    sql = """
        INSERT INTO teachers (name, employee_id, max_periods_per_week, is_international,
                              can_supervise_study_hours, departments, preferred_periods,
                              unavailable_periods, notes)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id, name, employee_id, max_periods_per_week, is_international,
                  can_supervise_study_hours, departments, preferred_periods,
                  unavailable_periods, notes;
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        name,
                        employee_id,
                        max_periods_per_week,
                        is_international,
                        can_supervise_study_hours,
                        Json(departments) if departments is not None else None,
                        Json((preferred_periods)) if preferred_periods is not None else None,
                        Json(unavailable_periods) if unavailable_periods is not None else None,
                        notes,
                    ),
                )
                row = cur.fetchone()
                return Teacher(*row)
    finally:
        conn.close()


def get_teacher(teacher_id: int) -> Optional[Teacher]:
    sql = """
        SELECT id, name, employee_id, max_periods_per_week, is_international,
               can_supervise_study_hours, departments, preferred_periods,
               unavailable_periods, notes
        FROM teachers WHERE id=%s
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (teacher_id,))
            row = cur.fetchone()
            return Teacher(*row) if row else None
    finally:
        conn.close()


def update_teacher(teacher_id: int, **fields) -> Teacher:
    if not fields:
        raise ValueError("No fields to update")
    columns = []
    values = []
    for key, value in fields.items():
        columns.append(f"{key}=%s")
        values.append(value)
    values.append(teacher_id)
    sql = f"""
        UPDATE teachers SET {', '.join(columns)} WHERE id=%s
        RETURNING id, name, employee_id, max_periods_per_week, is_international,
                  can_supervise_study_hours, departments, preferred_periods,
                  unavailable_periods, notes
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(values))
                row = cur.fetchone()
                return Teacher(*row)
    finally:
        conn.close()


def delete_teacher(teacher_id: int) -> bool:
    sql = "DELETE FROM teachers WHERE id=%s"
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, (teacher_id,))
                return cur.rowcount > 0
    finally:
        conn.close()
