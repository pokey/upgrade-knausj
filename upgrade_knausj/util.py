import contextlib
import os
import sys

from rich import print


# From https://stackoverflow.com/a/24469659/2605678
@contextlib.contextmanager
def cd(path):
    old_path = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_path)


def error_and_exit(message: str):
    print_error(message)
    sys.exit(1)


def print_error(message: str):
    print(f":x: [bold red]Error[/bold red] {message}")


def print_slack_help_info(message: str, extra_empty_line: bool = False):
    end = "\n\n" if extra_empty_line else "\n"
    print(
        f"[bold yellow]If {message}, please ask on the #upgrade-knausj "
        f"channel on the [link=https://talonvoice.com/chat]Talon slack workspace[/link] :smiling_face_with_smiling_eyes:[/bold yellow]",
        end=end,
    )
