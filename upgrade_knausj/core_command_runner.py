from typing import Sequence

import typer

from upgrade_knausj.command_runner import CommandRunner
from upgrade_knausj.printer import Printer
from upgrade_knausj.step import Step


class UnmetPreconditionError(Exception):
    step_name: str
    message: str

    def __init__(self, step_name, message) -> None:
        super().__init__(f"Error running '{step_name}':\n{message}")
        self.step_name = step_name
        self.message = message


class CoreCommandRunner(CommandRunner):
    _steps: Sequence[Step]
    _printer: Printer

    def __init__(self, printer: Printer, steps: Sequence[Step]):
        self._steps = steps
        self._printer = printer

    def __call__(self) -> None:
        for step in self._steps:
            if step.postcondition().success:
                self._printer.info(f"Already completed step '{step.name}'; skipping")
                continue

            precondition_result = step.precondition()

            if not precondition_result.success:
                raise UnmetPreconditionError(step.name, precondition_result.message)

            self._printer.info(f"Running '{step.name}'...")
            step.run()
