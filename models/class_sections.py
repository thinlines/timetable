from dataclasses import dataclass
from typing import Optional

from db import get_connection


@dataclass
class ClassSection:
    id: Optional[int]
    course_id: Optional[int]
    section_name: Optional[str]
    max_students: int = 24
    semester: Optional[str] = None
    is_active: bool = True


def create_class_section(
    course_id: Optional[int] = None,
    section_name: Optional[str] = None,
    max_students: int = 24,
    semester: Optional[str] = None,
    is_active: bool = True,
) -> ClassSection:
    sql = """
        INSERT INTO class_sections (course_id, section_name, max_students, semester, is_active)
        VALUES (%s,%s,%s,%s,%s)
        RETURNING id, course_id, section_name, max_students, semester, is_active;
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (course_id, section_name, max_students, semester, is_active),
                )
                row = cur.fetchone()
                return ClassSection(*row)
    finally:
        conn.close()


def get_class_section(section_id: int) -> Optional[ClassSection]:
    sql = """
        SELECT id, course_id, section_name, max_students, semester, is_active
        FROM class_sections WHERE id=%s
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (section_id,))
            row = cur.fetchone()
            return ClassSection(*row) if row else None
    finally:
        conn.close()


def update_class_section(section_id: int, **fields) -> ClassSection:
    if not fields:
        raise ValueError("No fields to update")
    cols = []
    vals = []
    for k, v in fields.items():
        cols.append(f"{k}=%s")
        vals.append(v)
    vals.append(section_id)
    sql = f"""
        UPDATE class_sections SET {', '.join(cols)} WHERE id=%s
        RETURNING id, course_id, section_name, max_students, semester, is_active
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(vals))
                row = cur.fetchone()
                return ClassSection(*row)
    finally:
        conn.close()


def delete_class_section(section_id: int) -> bool:
    sql = "DELETE FROM class_sections WHERE id=%s"
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, (section_id,))
                return cur.rowcount > 0
    finally:
        conn.close()
