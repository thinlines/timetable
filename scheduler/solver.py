from __future__ import annotations

import json
from typing import Dict, List, Tuple

from ortools.sat.python import cp_model
from repository import (
    Assignment,
    fetch_class_sections,
    fetch_facilities,
    fetch_periods,
    fetch_teachers,
    fetch_teacher_course_map,
    fetch_international_teacher_ids,
    persist_schedule,
)
from scheduler.utils import coerce_json


def solve() -> List[Dict[str, int]]:
    """Solve the timetable problem and return the in-memory schedule."""
    # Data
    # class_sections: (section_id, periods_per_week, course_id)
    class_sections: List[Tuple[int, int, int]] = fetch_class_sections()
    teachers = fetch_teachers()
    facilities = fetch_facilities()
    periods = fetch_periods()  # (id, period_number, day_of_week)
    eligibility_map = fetch_teacher_course_map()  # course_id -> {teacher_id}
    has_eligibility = bool(eligibility_map)
    international_teachers = fetch_international_teacher_ids()

    model = cp_model.CpModel()

    # Utility to get eligible teachers for a course
    def eligible_teachers(course_id: int):
        if not has_eligibility:
            return teachers
        allowed = eligibility_map.get(course_id)
        if not allowed:
            # If eligibility data exists but none listed for this course, allow all
            return teachers
        return [t for t in teachers if t[0] in allowed]

    # Decision vars include a meeting index m in [0, periods_per_week)
    # Key: (section_id, meeting_idx, teacher_id, facility_id, period_id)
    vars: Dict[Tuple[int, int, int, int, int], cp_model.IntVar] = {}
    forbidden_vars: List[cp_model.IntVar] = []

    # Precompute first/last period numbers for each day
    day_bounds: Dict[int, Tuple[int, int]] = {}
    for _id, period_no, day in periods:
        if day is None or period_no is None:
            # If missing metadata, skip special handling
            continue
        lo, hi = day_bounds.get(day, (period_no, period_no))
        lo = min(lo, period_no)
        hi = max(hi, period_no)
        day_bounds[day] = (lo, hi)
    for (sec_id, ppw, course_id) in class_sections:
        elig_teachers = eligible_teachers(course_id)
        for m in range(ppw):
            for t in elig_teachers:
                for f in facilities:
                    for p in periods:
                        key = (sec_id, m, t[0], f[0], p[0])
                        v = model.NewBoolVar(
                            f"c{sec_id}_m{m}_t{t[0]}_f{f[0]}_p{p[0]}"
                        )
                        vars[key] = v
                        # Forbid international teachers from first/last period of the day
                        if t[0] in international_teachers:
                            _, pno, day = p
                            if day in day_bounds:
                                lo, hi = day_bounds[day]
                                if pno in (lo, hi):
                                    forbidden_vars.append(v)

    # Each meeting of each section scheduled exactly once
    for (sec_id, ppw, course_id) in class_sections:
        elig_teachers = eligible_teachers(course_id)
        for m in range(ppw):
            model.Add(
                sum(
                    vars[(sec_id, m, t[0], f[0], p[0])]
                    for t in elig_teachers
                    for f in facilities
                    for p in periods
                )
                == 1
            )

    # No two meetings of the same section in the same period
    for (sec_id, ppw, course_id) in class_sections:
        elig_teachers = eligible_teachers(course_id)
        for p in periods:
            model.Add(
                sum(
                    vars[(sec_id, m, t[0], f[0], p[0])]
                    for m in range(ppw)
                    for t in elig_teachers
                    for f in facilities
                )
                <= 1
            )

    # Teacher load limits and one class per period
    for t in teachers:
        # Weekly load
        model.Add(
            sum(
                vars[(sec_id, m, t[0], f[0], p[0])]
                for (sec_id, ppw, course_id) in class_sections
                for m in range(ppw)
                for f in facilities
                for p in periods
                if (not has_eligibility) or (t[0] in eligibility_map.get(course_id, set())) or (course_id not in eligibility_map)
            )
            <= t[1]
        )
        # One class per period
        for p in periods:
            model.Add(
                sum(
                    vars[(sec_id, m, t[0], f[0], p[0])]
                    for (sec_id, ppw, course_id) in class_sections
                    for m in range(ppw)
                    for f in facilities
                    if (not has_eligibility) or (t[0] in eligibility_map.get(course_id, set())) or (course_id not in eligibility_map)
                )
                <= 1
            )

    # Facility conflicts
    for f in facilities:
        for p in periods:
            model.Add(
                sum(
                    vars[(sec_id, m, t[0], f[0], p[0])]
                    for (sec_id, ppw, course_id) in class_sections
                    for m in range(ppw)
                    for t in (eligible_teachers(course_id) if has_eligibility else teachers)
                )
                <= 1
            )

    # soft constraint: teacher preferred periods
    penalty_terms = []
    for (sec_id, ppw, course_id) in class_sections:
        for m in range(ppw):
            for t in eligible_teachers(course_id):
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
                        v = vars[(sec_id, m, t[0], f[0], p[0])]
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
            # key: (section_id, meeting_idx, teacher_id, facility_id, period_id)
            sec_id, _m, teacher_id, facility_id, period_id = key
            assignments.append((sec_id, teacher_id, facility_id, period_id))
            schedule.append(
                {
                    "class_section_id": sec_id,
                    "teacher_id": teacher_id,
                    "facility_id": facility_id,
                    "time_period_id": period_id,
                }
            )

    persist_schedule(assignments)
    return schedule
    # Apply forbidden variable constraints
    for v in forbidden_vars:
        model.Add(v == 0)
