from __future__ import annotations

import json
from typing import Dict, List

from ortools.sat.python import cp_model
from repository import (
    Assignment,
    fetch_class_sections,
    fetch_facilities,
    fetch_periods,
    fetch_teachers,
    persist_schedule,
)
from scheduler.utils import coerce_json


def solve() -> List[Dict[str, int]]:
    """Solve the timetable problem and return the in-memory schedule."""
    class_sections = fetch_class_sections()
    teachers = fetch_teachers()
    facilities = fetch_facilities()
    periods = fetch_periods()

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
            pref_periods = set()
            if t[2]:
                try:
                    data = coerce_json(t[2])
                    if isinstance(data, dict):
                        pref_periods = set(data.get("preferred", []))
                    elif isinstance(data, list):
                        pref_periods = set(data)
                except json.JSONDecodeError:
                    pass
            for f in facilities:
                for p in periods:
                    v = vars[(c[0], t[0], f[0], p[0])]
                    if pref_periods and p[0] not in pref_periods:
                        penalty_terms.append(v)
    if penalty_terms:
        model.Minimize(sum(penalty_terms))

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

    persist_schedule(assignments)
    return schedule

