from dataclasses import dataclass
from typing import Optional, Dict, Any

from db import get_connection


@dataclass
class Course:
    id: Optional[int]
    code: str
    name: str
    department: Optional[str] = None
    periods_per_week: int = 1
    is_mandatory: bool = False
    is_elective: bool = False
    requires_consecutive_periods: bool = False
    preferred_facility_type: Optional[str] = None
    requires_specific_facility: bool = False
    grade_levels: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


def create_course(
    code: str,
    name: str,
    periods_per_week: int,
    department: Optional[str] = None,
    is_mandatory: bool = False,
    is_elective: bool = False,
    requires_consecutive_periods: bool = False,
    preferred_facility_type: Optional[str] = None,
    requires_specific_facility: bool = False,
    grade_levels: Optional[Dict[str, Any]] = None,
    notes: Optional[str] = None,
) -> Course:
    sql = """
        INSERT INTO courses (code, name, department, periods_per_week,
                             is_mandatory, is_elective, requires_consecutive_periods,
                             preferred_facility_type, requires_specific_facility,
                             grade_levels, notes)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id, code, name, department, periods_per_week,
                  is_mandatory, is_elective, requires_consecutive_periods,
                  preferred_facility_type, requires_specific_facility,
                  grade_levels, notes;
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        code,
                        name,
                        department,
                        periods_per_week,
                        is_mandatory,
                        is_elective,
                        requires_consecutive_periods,
                        preferred_facility_type,
                        requires_specific_facility,
                        grade_levels,
                        notes,
                    ),
                )
                row = cur.fetchone()
                return Course(*row)
    finally:
        conn.close()


def get_course(course_id: int) -> Optional[Course]:
    sql = """
        SELECT id, code, name, department, periods_per_week,
               is_mandatory, is_elective, requires_consecutive_periods,
               preferred_facility_type, requires_specific_facility,
               grade_levels, notes
        FROM courses WHERE id=%s
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (course_id,))
            row = cur.fetchone()
            return Course(*row) if row else None
    finally:
        conn.close()


def update_course(course_id: int, **fields) -> Course:
    if not fields:
        raise ValueError("No fields to update")
    cols = []
    vals = []
    for k, v in fields.items():
        cols.append(f"{k}=%s")
        vals.append(v)
    vals.append(course_id)
    sql = f"""
        UPDATE courses SET {', '.join(cols)} WHERE id=%s
        RETURNING id, code, name, department, periods_per_week,
                  is_mandatory, is_elective, requires_consecutive_periods,
                  preferred_facility_type, requires_specific_facility,
                  grade_levels, notes
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(vals))
                row = cur.fetchone()
                return Course(*row)
    finally:
        conn.close()


def delete_course(course_id: int) -> bool:
    sql = "DELETE FROM courses WHERE id=%s"
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, (course_id,))
                return cur.rowcount > 0
    finally:
        conn.close()
