#!/usr/bin/env python3
import yaml
import sys
import pandas as pd
import random

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIODS = list(range(1, 10))


def load_config(filename="config.yaml"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        sys.exit(f"Error loading config.yaml: {e}")


def schedule_timetables(config):
    teachers = {t["id"]: t["name"] for t in config.get("teachers", [])}
    courses = {
        c["id"]: {"name": c["name"], "teacher_id": c["teacher_id"]}
        for c in config.get("courses", [])
    }
    teacher_limits = config.get("teacher_limits", {})

    timetables = {
        class_name: {(day, period): None for day in DAYS for period in PERIODS}
        for class_name in config["classes"]
    }

    global_assignments = {}

    for teacher_id in teachers:
        global_assignments[teacher_id] = []

    for class_name, class_info in config["classes"].items():
        for course_assignment in class_info.get("courses", []):
            course_id = course_assignment["course_id"]
            periods = course_assignment["periods_per_week"]
            course = courses.get(course_id)
            if not course:
                continue

            teacher_id = course["teacher_id"]

            for _ in range(periods):
                available_slots = [
                    (day, period)
                    for day in DAYS
                    for period in PERIODS
                    if timetables[class_name][(day, period)] is None
                ]
                random.shuffle(available_slots)

                for day, period in available_slots:
                    if len(global_assignments[teacher_id]) >= teacher_limits.get(
                        teacher_id, 15
                    ):
                        continue

                    timetables[class_name][(day, period)] = {
                        "course": course["name"],
                        "teacher": teachers[teacher_id],
                    }
                    global_assignments[teacher_id].append((day, period))
                    break

    return timetables


def output_timetable(timetables):
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


def main():
    config = load_config()
    timetable = schedule_timetables(config)
    output_timetable(timetable)


if __name__ == "__main__":
    main()
