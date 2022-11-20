from rich import print
from rich.console import Console


class Printer:
    _err_console: Console

    def __init__(self):
        self._err_console = Console(stderr=True)

    def error(self, msg):
        self._err_console.print(f":x: [bold red]Error[/bold red]: {msg}")

    def info(self, msg):
        print(msg)
