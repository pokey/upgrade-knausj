from upgrade_knausj.core_command_runner import UnmetConditionError
from upgrade_knausj.stdio.printer import Printer
from upgrade_knausj.types.command_runner import CommandRunner


class ErrorPrintingRunner(CommandRunner):
    _runner: CommandRunner
    _printer: Printer

    def __init__(self, printer: Printer, runner: CommandRunner):
        self._runner = runner
        self._printer = printer

    def __call__(self) -> None:
        try:
            self._runner()
        except UnmetConditionError as err:
            self._printer.error(
                f"'{err.step_name}' {err.condition_type} not met:\n  :right_arrow: {err.message}"
            )
