from dataclasses import dataclass
from typing import Optional

from db import get_connection


@dataclass
class Facility:
    id: Optional[int]
    name: str
    facility_type: Optional[str] = None
    capacity: int = 24
    can_split: bool = False
    split_capacity: Optional[int] = None
    notes: Optional[str] = None


def create_facility(
    name: str,
    facility_type: Optional[str] = None,
    capacity: int = 24,
    can_split: bool = False,
    split_capacity: Optional[int] = None,
    notes: Optional[str] = None,
) -> Facility:
    sql = """
        INSERT INTO facilities (name, facility_type, capacity, can_split, split_capacity, notes)
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING id, name, facility_type, capacity, can_split, split_capacity, notes;
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    sql,
                    (name, facility_type, capacity, can_split, split_capacity, notes),
                )
                row = cur.fetchone()
                return Facility(*row)
    finally:
        conn.close()


def get_facility(facility_id: int) -> Optional[Facility]:
    sql = """
        SELECT id, name, facility_type, capacity, can_split, split_capacity, notes
        FROM facilities WHERE id=%s
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (facility_id,))
            row = cur.fetchone()
            return Facility(*row) if row else None
    finally:
        conn.close()


def update_facility(facility_id: int, **fields) -> Facility:
    if not fields:
        raise ValueError("No fields to update")
    cols = []
    vals = []
    for k, v in fields.items():
        cols.append(f"{k}=%s")
        vals.append(v)
    vals.append(facility_id)
    sql = f"""
        UPDATE facilities SET {', '.join(cols)} WHERE id=%s
        RETURNING id, name, facility_type, capacity, can_split, split_capacity, notes
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(vals))
                row = cur.fetchone()
                return Facility(*row)
    finally:
        conn.close()


def delete_facility(facility_id: int) -> bool:
    sql = "DELETE FROM facilities WHERE id=%s"
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, (facility_id,))
                return cur.rowcount > 0
    finally:
        conn.close()
