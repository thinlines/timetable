from __future__ import annotations

import json
from typing import Dict, List, Tuple

from ortools.sat.python import cp_model
from db import get_connection
from scheduler.utils import coerce_json

Assignment = Tuple[int, int, int, int]  # class_section_id, teacher_id, facility_id, period_id


def _fetch_all(table: str, columns: List[str]) -> List[Tuple]:
    """Generic helper to fetch all rows from ``table`` for ``columns``."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(columns)} FROM {table}")
            return cur.fetchall()
    finally:
        conn.close()


def _store_schedule(assignments: List[Assignment]) -> None:
    """Persist schedule into ``scheduled_classes`` and ``class_enrollments`` tables."""
    if not assignments:
        return

    students = _fetch_all("students", ["id"])
    student_ids = [s[0] for s in students]
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                for class_id, teacher_id, facility_id, period_id in assignments:
                    # fetch semester from class_section
                    cur.execute(
                        "SELECT semester FROM class_sections WHERE id=%s", (class_id,)
                    )
                    semester = cur.fetchone()[0]
                    cur.execute(
                        """
                        INSERT INTO scheduled_classes
                            (class_section_id, teacher_id, facility_id, time_period_id, semester)
                        VALUES (%s,%s,%s,%s,%s)
                        RETURNING id;
                        """,
                        (class_id, teacher_id, facility_id, period_id, semester),
                    )
                    scheduled_id = cur.fetchone()[0]
                    for sid in student_ids:
                        cur.execute(
                            "INSERT INTO class_enrollments (scheduled_class_id, student_id) VALUES (%s,%s)",
                            (scheduled_id, sid),
                        )
    finally:
        conn.close()


def solve() -> List[Dict[str, int]]:
    """Solve the timetable problem and return the in-memory schedule."""
    class_sections = _fetch_all("class_sections", ["id"])
    teachers = _fetch_all(
        "teachers", ["id", "max_periods_per_week", "preferred_periods"]
    )
    facilities = _fetch_all("facilities", ["id"])
    periods = _fetch_all("time_periods", ["id"])

    # pre-parse teacher preferred periods so we can reference them in multiple
    # constraint sections.  ``preferred_periods`` is stored as JSON in the DB
    # and may come back either as a JSON string or an already decoded Python
    # object.  Normalising it here makes the subsequent model building logic
    # clearer and avoids repeatedly parsing the JSON inside nested loops.
    teacher_pref_periods: Dict[int, set[int]] = {}
    for t in teachers:
        pref_periods: set[int] = set()
        if t[2]:
            try:
                data = coerce_json(t[2])
                if isinstance(data, dict):
                    pref_periods = set(data.get("preferred", []))
                elif isinstance(data, list):
                    pref_periods = set(data)
            except json.JSONDecodeError:
                # Ignore invalid JSON – treat as having no preferred periods.
                pass
        teacher_pref_periods[t[0]] = pref_periods

    model = cp_model.CpModel()

    vars: Dict[Assignment, cp_model.IntVar] = {}
    for c in class_sections:
        for t in teachers:
            for f in facilities:
                for p in periods:
                    vars[(c[0], t[0], f[0], p[0])] = model.NewBoolVar(
                        f"c{c[0]}_t{t[0]}_f{f[0]}_p{p[0]}"
                    )

    # each class scheduled exactly once
    for c in class_sections:
        model.Add(
            sum(
                vars[(c[0], t[0], f[0], p[0])]
                for t in teachers
                for f in facilities
                for p in periods
            )
            == 1
        )

    # teacher load limits and one class per period
    for t in teachers:
        model.Add(
            sum(
                vars[(c[0], t[0], f[0], p[0])]
                for c in class_sections
                for f in facilities
                for p in periods
            )
            <= t[1]
        )
        for p in periods:
            model.Add(
                sum(
                    vars[(c[0], t[0], f[0], p[0])]
                    for c in class_sections
                    for f in facilities
                )
                <= 1
            )

    # facility conflicts
    for f in facilities:
        for p in periods:
            model.Add(
                sum(
                    vars[(c[0], t[0], f[0], p[0])]
                    for c in class_sections
                    for t in teachers
                )
                <= 1
            )

    # soft constraint: teacher preferred periods
    penalty_terms = []
    for c in class_sections:
        for t in teachers:
            pref_periods = teacher_pref_periods.get(t[0], set())
            for f in facilities:
                for p in periods:
                    v = vars[(c[0], t[0], f[0], p[0])]
                    # Penalise assignments that fall outside the teacher's
                    # preferred periods.  If a teacher has not specified any
                    # preferences we simply do not add the variable to the
                    # objective.
                    if pref_periods and p[0] not in pref_periods:
                        penalty_terms.append(v)
    if penalty_terms:
        model.Minimize(sum(penalty_terms))

    # Harder encouragement: if a teacher has listed preferred periods, force all
    # of their assignments to come from that set.  This still allows teachers
    # without preferences to be scheduled in any period while ensuring that the
    # solver honours stated preferences when possible.
    for t in teachers:
        pref_periods = teacher_pref_periods.get(t[0], set())
        if pref_periods:
            total_assignments = []
            preferred_assignments = []
            for c in class_sections:
                for f in facilities:
                    for p in periods:
                        v = vars[(c[0], t[0], f[0], p[0])]
                        total_assignments.append(v)
                        if p[0] in pref_periods:
                            preferred_assignments.append(v)
            # Require that any assignment for this teacher uses a preferred
            # period.  If the teacher isn't assigned at all this equality still
            # holds as both sides will be zero.
            model.Add(sum(total_assignments) == sum(preferred_assignments))

    solver = cp_model.CpSolver()
    result = solver.Solve(model)
    if result not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("No feasible schedule found")

    assignments: List[Assignment] = []
    schedule: List[Dict[str, int]] = []
    for key, var in vars.items():
        if solver.Value(var):
            assignments.append(key)
            schedule.append(
                {
                    "class_section_id": key[0],
                    "teacher_id": key[1],
                    "facility_id": key[2],
                    "time_period_id": key[3],
                }
            )

    _store_schedule(assignments)
    return schedule

