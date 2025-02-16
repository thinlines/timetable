#!/usr/bin/env python3
import yaml
import sys
import pandas as pd

# --- Data Structures and Helpers ---

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PERIODS = list(range(1, 10))  # 9 periods per day


def all_timeslots():
    slots = []
    for day in DAYS:
        for period in PERIODS:
            slots.append((day, period))
    return slots


def teacher_available(
    teacher,
    day,
    period, global_assignments, teacher_limits, default_teacher_limit
):
    # Ensure teacher is not scheduled elsewhere at the same time.
    if (day, period) in global_assignments.get(teacher, []):
        return False
    # Check teacher load/capacity.
    if len(global_assignments.get(teacher, [])) >= teacher_limits.get(
        teacher, default_teacher_limit
    ):
        return False
    return True

# --- Modified schedule_timetables ---
def schedule_timetables(
    classes_config,
    courses_config,
    teacher_constraints,
    cotaught,
    teacher_limits,
    default_teacher_limit=24,
    fixed_events=None,
):
    """
    Build a timetable for each class.
    Timetable for each class is a dict: {(day, period): assignment}
    where assignment is either None (free slot) or a dict with course info.
    """
    # Mapping from course_id to course definition.
    course_map = {course["id"]: course for course in courses_config}

    # Initialize timetable for each class.
    timetables = {
        class_name: {(day, period): None for day in DAYS for period in PERIODS}
        for class_name in classes_config.keys()
    }

    # Preassign fixed events (applied to all classes).
    if fixed_events:
        for event in fixed_events:
            day = event["day"]
            period = event["period"]
            course = event["course"]
            for tt in timetables.values():
                tt[(day, period)] = {"course": course, "teacher": None}

    # Initialize global mapping for teacher assignments.
    global_assignments = {}

    # Preassign teacher constraints (positive fixed assignments).
    # Now each constraint is expected to include 'class' and 'course'.
    for teacher, constraints in teacher_constraints.items():
        for constraint in constraints:
            class_name = constraint["class"]
            day = constraint["day"]
            period = constraint["period"]
            course = constraint["course"]
            if timetables[class_name][(day, period)] is None:
                timetables[class_name][(day, period)] = {
                    "course": course,
                    "teacher": teacher,
                }
                global_assignments.setdefault(teacher, []).append((day, period))

    # Build tasks for the remaining periods to schedule.
    tasks = []
    for class_name, class_info in classes_config.items():
        for course_assignment in class_info.get("courses", []):
            course_id = course_assignment["course_id"]
            periods = course_assignment["periods_per_week"]
            course_def = course_map.get(course_id)
            if not course_def:
                print(
                    f"Warning: course id {course_id} not found for class {class_name}"
                )
                continue
            candidate_teachers = course_def.get("teachers", [])
            # Subtract any preassigned teacher constraints for this class/course.
            constraint_count = 0
            for teacher, constraints in teacher_constraints.items():
                for constraint in constraints:
                    if (
                        constraint.get("class") == class_name
                        and constraint.get("course") == course_def["name"]
                    ):
                        constraint_count += 1
            remaining_periods = periods - constraint_count
            remaining_periods = max(remaining_periods, 0)
            for _ in range(remaining_periods):
                tasks.append(
                    {
                        "class": class_name,
                        "course": course_def["name"],
                        "teachers": candidate_teachers,
                    }
                )

    # Backtracking algorithm (unchanged except for calling teacher_available with new args).
    def backtrack(task_index, tasks, timetables, global_assignments):
        if task_index == len(tasks):
            return True  # All tasks scheduled
        task = tasks[task_index]
        class_name = task["class"]

        # Gather free timeslots (skip fixed assignments).
        available_slots = [
            timeslot
            for timeslot, current in timetables[class_name].items()
            if current is None
        ]

        # Sort candidate teachers by current load.
        candidate_teachers = sorted(
            task["teachers"], key=lambda t: len(global_assignments.get(t, []))
        )

        for slot in available_slots:
            day, period = slot
            for teacher in candidate_teachers:
                if not teacher_available(
                    teacher,
                    day,
                    period,
                    global_assignments,
                    teacher_limits,
                    default_teacher_limit,
                ):
                    continue

                timetables[class_name][slot] = {
                    "course": task["course"],
                    "teacher": teacher,
                }
                global_assignments.setdefault(teacher, []).append(slot)

                # Cotaught logic remains the same.
                cotaught_ok = True
                for ct in cotaught:
                    if ct.get("course") == task["course"]:
                        if class_name in ct.get("classes", []):
                            for other_class in ct.get("classes", []):
                                if other_class == class_name:
                                    continue
                                if timetables[other_class].get(slot) is not None:
                                    cotaught_ok = False
                                    break
                                other_teacher = ct.get("teachers", {}).get(other_class)
                                if other_teacher and not teacher_available(
                                    other_teacher,
                                    day,
                                    period,
                                    global_assignments,
                                    teacher_limits,
                                    default_teacher_limit,
                                ):
                                    cotaught_ok = False
                                    break
                            if not cotaught_ok:
                                break

                if cotaught_ok:
                    if backtrack(task_index + 1, tasks, timetables, global_assignments):
                        return True

                # Undo assignment.
                timetables[class_name][slot] = None
                global_assignments[teacher].remove(slot)
        return False

    if backtrack(0, tasks, timetables, global_assignments):
        return timetables
    else:
        return None

# --- Excel Output using Pandas with a Multi-Level Index ---

def output_to_excel_pandas(timetables, filename="timetable.xlsx"):
    """
    Create a single Excel sheet with a multi-level row index.
    The outer level is the period (1-9) and the inner level is the class (e.g., G10, G11, G12).
    The columns represent the days of the week.
    """
    # Build rows for the DataFrame: each row represents a (Period, Class) pair.
    rows = []
    for period in PERIODS:
        for class_name, schedule in timetables.items():
            row_data = {}
            for day in DAYS:
                assignment = schedule.get((day, period))
                if assignment is None:
                    cell_value = "Free"
                else:
                    if assignment.get("teacher"):
                        cell_value = f"{assignment['course']} ({assignment['teacher']})"
                    else:
                        cell_value = assignment["course"]
                row_data[day] = cell_value
            rows.append((period, class_name, row_data))
    # Create the MultiIndex: outer level = Period, inner level = Class.
    index = pd.MultiIndex.from_tuples(
        [(r[0], r[1]) for r in rows], names=["Period", "Class"]
    )
    df = pd.DataFrame([r[2] for r in rows], index=index, columns=DAYS)
    df.to_excel(filename)
    print(f"Timetable exported to {filename} using pandas.")

# --- Main Program ---

def main():
    try:
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        sys.exit(f"Error loading config.yaml: {e}")

    classes_config = config.get("classes", {})
    teacher_constraints = config.get("teacher_constraints", {})
    cotaught = config.get("cotaught", [])
    courses_config = config.get("courses", [])
    teacher_limits = config.get("teacher_limits", {})  # Optional teacher capacity overrides
    default_teacher_limit = 24  # Default maximum periods per week per teacher

    timetable = schedule_timetables(
        classes_config,
        courses_config,
        teacher_constraints,
        cotaught,
        teacher_limits,
        default_teacher_limit,
    )
    if timetable:
        # Optionally print the timetable to the console.
        for class_name, tt in timetable.items():
            print(f"\nTimetable for {class_name}:")
            for day in DAYS:
                print(day + ":")
                for period in PERIODS:
                    slot = (day, period)
                    entry = tt.get(slot)
                    if entry:
                        if entry["teacher"]:
                            print(
                                f"  Period {period}: {entry['course']} (Teacher: {entry['teacher']})"
                            )
                        else:
                            print(f"  Period {period}: {entry['course']}")
                    else:
                        print(f"  Period {period}: Free")
        # Use pandas to export the timetable with a multi-level index.
        output_to_excel_pandas(timetable)
    else:
        print("No valid timetable configuration found with the given constraints.")

if __name__ == "__main__":
    main()