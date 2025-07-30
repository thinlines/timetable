#!/usr/bin/env python3
"""Utility functions for displaying generated schedules."""

from __future__ import annotations
from typing import Dict, Tuple

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIODS = list(range(1, 10))


def output_timetable(timetables: Dict[str, Dict[Tuple[str, int], Dict[str, str]]]):
    """Print the timetable for each class."""
    for class_name, tt in timetables.items():
        print(f"\nTimetable for {class_name}:")
        for day in DAYS:
            print(day + ":")
            for period in PERIODS:
                entry = tt.get((day, period))
                if entry:
                    print(
                        f"  Period {period}: {entry['course']} (Teacher: {entry['teacher']})"
                    )
                else:
                    print(f"  Period {period}: Free")


def output_teacher_schedule(timetables: Dict[str, Dict[Tuple[str, int], Dict[str, str]]], teacher: str):
    """Print the weekly schedule for a given teacher name."""
    schedule: Dict[Tuple[str, int], Tuple[str, str]] = {}
    for class_name, tt in timetables.items():
        for (day, period), entry in tt.items():
            if entry and entry.get("teacher") == teacher:
                schedule[(day, period)] = (class_name, entry["course"])

    print(f"\nSchedule for {teacher}:")
    for day in DAYS:
        print(day + ":")
        for period in PERIODS:
            cls_course = schedule.get((day, period))
            if cls_course:
                cls, course = cls_course
                print(f"  Period {period}: {course} with {cls}")
            else:
                print(f"  Period {period}: Free")
