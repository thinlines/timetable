import os
from typing import Optional

import psycopg2


def get_connection():
    """Create a new database connection using environment variables."""
    conn = psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB", "postgres"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=os.environ.get("POSTGRES_PORT", 5432),
    )
    conn.autocommit = True
    return conn


def init_db():
    """Initialise the database using the schema.sql file."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;")
    statement = ""
    with open("schema.sql") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("--"):
                continue
            if line.startswith("SET ") or line.startswith("SELECT pg_catalog"):
                continue
            statement += " " + line
            if line.endswith(";"):
                if "OWNER TO" in statement:
                    statement = ""
                    continue
                try:
                    cur.execute(statement)
                except psycopg2.Error:
                    pass
                statement = ""
    cur.close()
    conn.close()


def get_students():
    """Return all students from the database."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, student_id, name, grade_level FROM students")
        rows = cur.fetchall()
    conn.close()
    return rows


def display_students():
    """Print the students table to stdout."""
    for row in get_students():
        print(row)


def add_student(student_id: str, name: str, grade_level: int):
    """Insert a new student and return the created row (id, student_id, name, grade_level)."""
    sql = """
        INSERT INTO students (student_id, name, grade_level)
        VALUES (%s, %s, %s)
        RETURNING id, student_id, name, grade_level;
    """
    conn = get_connection()
    try:
        with conn:  # commits on success, rollbacks on exception
            with conn.cursor() as cur:
                cur.execute(sql, (student_id, name, grade_level))
                row = cur.fetchone()
                return row
    finally:
        conn.close()


def get_student(student_id: str):
    """Fetch a single student row by ``student_id``."""
    sql = (
        "SELECT id, student_id, name, grade_level FROM students WHERE student_id=%s"
    )
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (student_id,))
            return cur.fetchone()
    finally:
        conn.close()


def update_student(
    student_id: str, name: Optional[str] = None, grade_level: Optional[int] = None
):
    """
    Update an existing student and return the updated row.

    At least one of ``name`` or ``grade_level`` must be provided.
    """

    fields = []
    values = []
    if name is not None:
        fields.append("name=%s")
        values.append(name)
    if grade_level is not None:
        fields.append("grade_level=%s")
        values.append(grade_level)
    if not fields:
        raise ValueError("No fields to update")
    values.append(student_id)

    sql = f"""
        UPDATE students
        SET {', '.join(fields)}
        WHERE student_id=%s
        RETURNING id, student_id, name, grade_level;
    """

    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(values))
                return cur.fetchone()
    finally:
        conn.close()


def delete_student(student_id: str) -> bool:
    """Delete a student by ``student_id``. Returns ``True`` if a row was deleted."""
    sql = "DELETE FROM students WHERE student_id=%s"
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, (student_id,))
                return cur.rowcount > 0
    finally:
        conn.close()
