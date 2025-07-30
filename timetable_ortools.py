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


def build_model(config: Dict) -> Tuple[cp_model.CpModel, Dict[Tuple[str, int, str, int], cp_model.IntVar]]:
    model = cp_model.CpModel()

    # Map (class, course, day, period) -> binary variable
    variables: Dict[Tuple[str, int, str, int], cp_model.IntVar] = {}

    for class_name, class_info in config["classes"].items():
        for course in class_info.get("courses", []):
            course_id = course["course_id"]
            for day in DAYS:
                for period in PERIODS:
                    var_name = f"x_{class_name}_{course_id}_{day}_{period}"
                    variables[(class_name, course_id, day, period)] = model.NewBoolVar(var_name)

    # Each class can only have one course in a period
    for class_name in config["classes"]:
        for day in DAYS:
            for period in PERIODS:
                model.Add(
                    sum(
                        variables[(class_name, c["course_id"], day, period)]
                        for c in config["classes"][class_name].get("courses", [])
                    )
                    <= 1
                )

    # Teachers teach at most one class per period
    teacher_courses: Dict[int, List[Tuple[str, int]]] = collections.defaultdict(list)
    courses = {c["id"]: c for c in config.get("courses", [])}
    for class_name, class_info in config["classes"].items():
        for course in class_info.get("courses", []):
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
    for class_name, class_info in config["classes"].items():
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
    model, vars_ = build_model(config)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise RuntimeError("No feasible schedule found")

    # Build timetable dict similar to timetable.py
    timetables = {
        class_name: {(day, period): None for day in DAYS for period in PERIODS}
        for class_name in config["classes"]
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


if __name__ == "__main__":
    cfg = load_config()
    timetable = solve_timetable(cfg)
    # Reuse output_timetable from timetable.py for printing if available
    from timetable import output_timetable

    output_timetable(timetable)
