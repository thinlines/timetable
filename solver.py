"""Placeholder solver and export helpers."""
from typing import Iterable, List

from db import get_students


def run_solver(semester: str) -> List[tuple]:
    """Run the scheduling solver.

    Currently this is a placeholder that simply retrieves students from the
    repository layer to demonstrate integration.
    """
    students = get_students()
    # A real solver would build a timetable here
    print(f"Running solver for semester {semester} with {len(students)} students")
    return students


def export_schedule(semester: str, output_format: str) -> str:
    """Export schedule in the requested format.

    This placeholder converts the solver output to CSV or JSON.
    """
    data = run_solver(semester)
    if output_format.lower() == "json":
        import json

        return json.dumps(data)
    else:
        import csv
        import io

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        for row in data:
            writer.writerow(row)
        return buffer.getvalue()
