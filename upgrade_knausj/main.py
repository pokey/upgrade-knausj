from pathlib import Path

import typer

from upgrade_knausj.ask_for_origin_uri import AskForOriginUri
from upgrade_knausj.core_command_runner import CoreCommandRunner
from upgrade_knausj.error_printing_runner import ErrorPrintingRunner
from upgrade_knausj.repository import Repository
from upgrade_knausj.stdio.printer import Printer
from upgrade_knausj.stdio.prompter import Prompter
from upgrade_knausj.steps.add_remote import AddOrigin, AddUpstream
from upgrade_knausj.steps.create_repo import CreateRepo
from upgrade_knausj.steps.fetch_remote import FetchOrigin, FetchUpstream

app = typer.Typer()

repo_path = Path.home() / "knausj_staging"

# FIXME: Support http url
knausj_uri = "git@github.com:knausj85/knausj_talon.git"


@app.command()
def main():
    """
    Upgrade knausj
    """
    printer = Printer()
    prompter = Prompter()
    repository = Repository(repo_path)

    steps = [
        CreateRepo(repository),
        AddOrigin(repository, AskForOriginUri(prompter)),
        AddUpstream(repository, knausj_uri),
        FetchOrigin(repository),
        FetchUpstream(repository),
        # CheckoutOrigin(repository),
        # CheckoutUpstream(repository),
    ]

    runner = ErrorPrintingRunner(printer, CoreCommandRunner(printer, steps))

    runner()
