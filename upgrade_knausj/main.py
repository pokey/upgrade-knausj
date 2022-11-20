from pathlib import Path

import typer

from upgrade_knausj.core_command_runner import CoreCommandRunner
from upgrade_knausj.error_printing_runner import ErrorPrintingRunner
from upgrade_knausj.printer import Printer
from upgrade_knausj.steps.clone_repo import InitializeRepo

app = typer.Typer()

repo_path = Path.home() / "knausj_staging"


@app.command()
def main():
    """
    Upgrade knausj
    """
    printer = Printer()

    steps = [InitializeRepo(repo_path)]

    runner = ErrorPrintingRunner(printer, CoreCommandRunner(printer, steps))

    runner()
