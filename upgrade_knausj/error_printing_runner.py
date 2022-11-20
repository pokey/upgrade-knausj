from upgrade_knausj.command_runner import CommandRunner
from upgrade_knausj.core_command_runner import UnmetPreconditionError
from upgrade_knausj.printer import Printer


class ErrorPrintingRunner(CommandRunner):
    _runner: CommandRunner
    _printer: Printer

    def __init__(self, printer: Printer, runner: CommandRunner):
        self._runner = runner
        self._printer = printer

    def __call__(self) -> None:
        try:
            self._runner()
        except UnmetPreconditionError as err:
            self._printer.error(
                f"'{err.step_name}' precondition not met:\n  :right_arrow: {err.message}"
            )
