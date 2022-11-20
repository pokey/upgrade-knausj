from typing import Sequence

from upgrade_knausj.stdio.printer import Printer
from upgrade_knausj.types.command_runner import CommandRunner
from upgrade_knausj.types.step import Step


class UnmetConditionError(Exception):
    step_name: str
    message: str
    condition_type: str

    def __init__(self, condition_type: str, step_name: str, message: str) -> None:
        super().__init__(f"Error running '{step_name}':\n{message}")
        self.step_name = step_name
        self.message = message
        self.condition_type = condition_type


class CoreCommandRunner(CommandRunner):
    _steps: Sequence[Step]
    _printer: Printer

    def __init__(self, printer: Printer, steps: Sequence[Step]):
        self._steps = steps
        self._printer = printer

    def __call__(self) -> None:
        for step in self._steps:
            precondition_result = step.precondition()
            if not precondition_result.success:
                raise UnmetConditionError(
                    "precondition", step.name, precondition_result.message
                )

            if not step.always_run and step.postcondition().success:
                self._printer.info(f"Already completed step '{step.name}'; skipping")
                continue

            self._printer.info(f"Running '{step.name}'...")
            step()

            if not step.postcondition().success:
                raise UnmetConditionError(
                    "postcondition", step.name, precondition_result.message
                )
