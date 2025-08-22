import click

from db import init_db
from solver import run_solver, export_schedule

@click.group()
def cli():
    """Command line interface for the timetable system."""
    pass

@cli.command("populate-db")
@click.option("--semester", required=True, help="Semester identifier")
def populate_db_command(semester: str):
    """Initialise and populate the database."""
    init_db()
    click.echo(f"Database initialised for semester {semester}.")

@cli.command("run-solver")
@click.option("--semester", required=True, help="Semester identifier")
def run_solver_command(semester: str):
    """Run the scheduling solver for a semester."""
    run_solver(semester)
    click.echo("Solver run complete.")

@cli.command("export-schedule")
@click.option("--semester", required=True, help="Semester identifier")
@click.option(
    "--format",
    "format_",
    default="csv",
    show_default=True,
    type=click.Choice(["csv", "json"], case_sensitive=False),
    help="Output format",
)
def export_schedule_command(semester: str, format_: str):
    """Export the generated schedule."""
    export_schedule(semester, format_)
    click.echo(f"Schedule exported in {format_} format.")

if __name__ == "__main__":
    cli()
