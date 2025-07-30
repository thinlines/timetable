#!/usr/bin/env python3
"""Wrapper script that generates a timetable using OR-Tools."""

from timetable_ortools import load_config, solve_timetable
from schedule_output import output_timetable, output_teacher_schedule


def main() -> None:
    cfg = load_config()
    timetable = solve_timetable(cfg)
    output_timetable(timetable)
    for teacher in cfg["teachers"]:
        output_teacher_schedule(timetable, teacher["name"])


if __name__ == "__main__":
    main()
