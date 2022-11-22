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
    print(f":x: [bold red]Error[/bold red] {message}")
    sys.exit(1)
