#!/usr/bin/env python3
"""Prototype scheduler using OR-Tools CP-SAT.

This module demonstrates how we might transition from the current
random-assignment method to a solver-based approach.  It loads the same
configuration format as ``timetable.py`` but formulates the timetable
assignment as a constraint programming (CP-SAT) model with OR-Tools.
Only a minimal set of constraints is implemented at this stage.
"""

from __future__ import annotations

import collections
from typing import Dict, List, Tuple

import yaml
from ortools.sat.python import cp_model

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIODS = list(range(1, 10))


def load_config(filename: str = "config.yaml") -> Dict:
    with open(filename, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_config(config: Dict) -> Tuple[Dict[str, int], Dict[int, int]]:
    """Validate per-class and per-teacher period totals.

    Returns dictionaries mapping class names and teacher ids to the total
    requested periods.  Raises ``ValueError`` if any class or teacher exceeds
    the available capacity defined in the configuration.
    """

    total_slots = len(DAYS) * len(PERIODS)

    # Build lookups
    courses = {c["id"]: c for c in config.get("courses", [])}
    teacher_names = {t["id"]: t["name"] for t in config.get("teachers", [])}

    class_totals: Dict[str, int] = {}
    for class_name, class_info in config.get("course_requirements", {}).items():
        total = sum(c.get("periods_per_week", 0) for c in class_info)
        class_totals[class_name] = total
        if total > total_slots:
            raise ValueError(
                f"Class {class_name} requests {total} periods but only {total_slots} slots are available"
            )

    teacher_totals: Dict[int, int] = collections.defaultdict(int)
    for class_info in config.get("course_requirements", {}).values():
        for course in class_info:
            course_id = course["course_id"]
            periods = course.get("periods_per_week", 0)
            teacher_id = courses[course_id]["teacher_id"]
            teacher_totals[teacher_id] += periods

    limits = config.get("teacher_limits", {})
    for teacher_id, total in teacher_totals.items():
        limit = limits.get(teacher_id)
        if limit is not None and total > limit:
            name = teacher_names.get(teacher_id, str(teacher_id))
            raise ValueError(
                f"Teacher {name} assigned {total} periods which exceeds the limit of {limit}"
            )

    return class_totals, dict(teacher_totals)


def build_model(config: Dict) -> Tuple[cp_model.CpModel, Dict[Tuple[str, int, str, int], cp_model.IntVar]]:
    model = cp_model.CpModel()

    # Map (class, course, day, period) -> binary variable
    variables: Dict[Tuple[str, int, str, int], cp_model.IntVar] = {}

    for class_name, courses in config["course_requirements"].items():
        for course in courses:
            course_id = course["course_id"]
            for day in DAYS:
                for period in PERIODS:
                    var_name = f"x_{class_name}_{course_id}_{day}_{period}"
                    variables[(class_name, course_id, day, period)] = model.NewBoolVar(var_name)

    # Each class can only have one course in a period
    for class_name in config["course_requirements"]:
        for day in DAYS:
            for period in PERIODS:
                model.Add(
                    sum(
                        variables[(class_name, c["course_id"], day, period)]
                        for c in config["course_requirements"][class_name]
                    )
                    <= 1
                )

    # Teachers teach at most one class per period
    teacher_courses: Dict[int, List[Tuple[str, int]]] = collections.defaultdict(list)
    courses = {c["id"]: c for c in config.get("courses", [])}
    for class_name, courses in config["course_requirements"].items():
        for course in courses:
            course_id = course["course_id"]
            teacher_id = courses[course_id]["teacher_id"]
            teacher_courses[teacher_id].append((class_name, course_id))

    for teacher_id, course_list in teacher_courses.items():
        for day in DAYS:
            for period in PERIODS:
                model.Add(
                    sum(
                        variables[(cls, cid, day, period)]
                        for cls, cid in course_list
                    )
                    <= 1
                )

    # Course frequency requirements
    for class_name, class_info in config["course_requirements"].items():
        for course in class_info.get("courses", []):
            course_id = course["course_id"]
            periods = course["periods_per_week"]
            model.Add(
                sum(
                    variables[(class_name, course_id, day, period)]
                    for day in DAYS
                    for period in PERIODS
                )
                <= periods
            )

    # Objective: maximise the number of scheduled lessons.
    model.Maximize(
        sum(var for var in variables.values())
    )

    return model, variables


def solve_timetable(config: Dict):
    class_totals, teacher_totals = validate_config(config)
    model, vars_ = build_model(config)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("Requested periods per class:")
        for cls, total in class_totals.items():
            print(f"  {cls}: {total} / {len(DAYS) * len(PERIODS)}")

        teacher_names = {t["id"]: t["name"] for t in config.get("teachers", [])}
        print("Requested periods per teacher:")
        for tid, total in teacher_totals.items():
            name = teacher_names.get(tid, str(tid))
            limit = config.get("teacher_limits", {}).get(tid)
            if limit is not None:
                print(f"  {name}: {total} / {limit}")
            else:
                print(f"  {name}: {total}")
        raise RuntimeError("No feasible schedule found")

    # Build timetable dict similar to timetable.py
    timetables = {
        class_name: {(day, period): None for day in DAYS for period in PERIODS}
        for class_name in config["course_requirements"]
    }

    courses = {c["id"]: c for c in config.get("courses", [])}

    for (class_name, course_id, day, period), var in vars_.items():
        if solver.Value(var) > 0:
            teacher_id = courses[course_id]["teacher_id"]
            timetables[class_name][(day, period)] = {
                "course": courses[course_id]["name"],
                "teacher": next(t["name"] for t in config["teachers"] if t["id"] == teacher_id),
            }

    return timetables


