from __future__ import annotations

import json
from typing import Dict, List, Tuple, Set

from ortools.sat.python import cp_model
from repository import (
    Assignment,
    fetch_class_sections,
    fetch_facilities,
    fetch_periods,
    fetch_teachers,
    fetch_teacher_course_map,
    fetch_international_teacher_ids,
    fetch_courses_require_consecutive,
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
    courses_need_double = fetch_courses_require_consecutive()

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

    # Precompute allowed period ids for international teachers (middle periods per day)
    day_to_periods: Dict[int, List[Tuple[int, int]]] = {}
    for pid, period_no, day in periods:
        if day is None or period_no is None:
            continue
        day_to_periods.setdefault(day, []).append((period_no, pid))
    intl_ok_period_ids: Set[int] = set()
    for day, items in day_to_periods.items():
        # sort by period number, then id for stability
        items.sort()
        if len(items) <= 2:
            # no middle period exists; none are allowed (strict interpretation)
            # but to avoid infeasibility when only two exist, we could relax.
            # For current tests we have 3 periods.
            continue
        # take all except first and last
        middle = items[1:-1]
        for _pno, pid in middle:
            intl_ok_period_ids.add(pid)
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
                            pid, _pno, _day = p
                            if pid not in intl_ok_period_ids:
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
    # soft constraint: prefer at least one double-period for courses that request it
    # For each such section, encourage occupying two consecutive periods on the same day.
    # Construct day->sorted period tuples for consecutive relationship checks
    day_to_sorted: Dict[int, List[Tuple[int, int]]] = {}
    for pid, pno, day in periods:
        if day is None or pno is None:
            continue
        day_to_sorted.setdefault(day, []).append((pno, pid))
    for day, items in day_to_sorted.items():
        items.sort()

    # Helper to sum usage of a section in a given period id
    def section_usage_in_period(sec_id: int, course_id: int, period_id: int):
        return sum(
            vars[(sec_id, m, t[0], f[0], period_id)]
            for m in range(next(ppw for (sid, ppw, cid) in class_sections if sid == sec_id))
            for t in (eligible_teachers(course_id) if has_eligibility else teachers)
            for f in facilities
            if (not has_eligibility)
            or (t[0] in eligibility_map.get(course_id, set()))
            or (course_id not in eligibility_map)
        )

    # Build double-period encouragement terms
    for (sec_id, ppw, course_id) in class_sections:
        if course_id not in courses_need_double or ppw < 2:
            continue
        y_pairs = []
        # For each day, consider consecutive period-number neighbors
        for day, items in day_to_sorted.items():
            if len(items) < 2:
                continue
            for idx in range(len(items) - 1):
                (pno_a, pid_a) = items[idx]
                (pno_b, pid_b) = items[idx + 1]
                if pno_b != pno_a + 1:
                    # Not consecutive numbers; skip
                    continue
                # y_pair indicates section occupies both pid_a and pid_b (any meetings)
                y_pair = model.NewBoolVar(f"sec{sec_id}_double_d{day}_p{pid_a}_{pid_b}")
                use_a = section_usage_in_period(sec_id, course_id, pid_a)
                use_b = section_usage_in_period(sec_id, course_id, pid_b)
                # y <= use_a and y <= use_b; y >= use_a + use_b - 1
                model.Add(y_pair <= use_a)
                model.Add(y_pair <= use_b)
                model.Add(y_pair >= use_a + use_b - 1)
                y_pairs.append(y_pair)

        has_double = model.NewBoolVar(f"sec{sec_id}_has_double")
        if y_pairs:
            # has_double is OR of y_pairs
            for y in y_pairs:
                model.Add(y <= has_double)
            model.Add(has_double <= sum(y_pairs))
        else:
            # No candidate adjacent pairs in calendar; force false
            model.Add(has_double == 0)

        # Penalize missing a double-period
        miss_double = model.NewBoolVar(f"sec{sec_id}_miss_double")
        model.Add(has_double + miss_double == 1)
        penalty_terms.append(miss_double)

    if penalty_terms:
        model.Minimize(sum(penalty_terms))

    # Apply forbidden variable constraints before solving
    for v in forbidden_vars:
        model.Add(v == 0)

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
