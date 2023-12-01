from pathlib import Path

import typer
from git.repo import Repo
from rich import print
from rich.prompt import Confirm

from upgrade_knausj.git import merge_exiting_on_conflict
from upgrade_knausj.handle_challenging_commit import (
    ChallengingCommit,
    handle_challenging_commit,
)
from upgrade_knausj.setup import setup_knausj, setup_mine
from upgrade_knausj.util import error_and_exit, print_slack_help_info

app = typer.Typer()

repo_base_path = Path.home() / "knausj_staging"

challenging_commits = [
    ChallengingCommit("2877a6849d75e5fa78c9453991a9235b4f6d9dcf", is_precommit=True),
    ChallengingCommit(
        "3bf4882fa0a05b22171e59118bd7c9640aae753a", is_precommit=True, needs_patch=True
    ),
    ChallengingCommit(
        "c8ae6f87acde5d433df25a17a4d203186f9fe319",
        is_precommit=False,
    ),
    ChallengingCommit(
        "446ec764c9caa98973eacd7f792b6a087a1b635f", is_precommit=True, needs_patch=True
    ),
    ChallengingCommit(
        "b25bac46c6543d0ec5fe2b2d09596444cd903371",
        is_precommit=False,
    ),
    ChallengingCommit(
        "4612817a0281ffdc698ba496d5a0530011bb5449", is_precommit=True, needs_patch=True
    ),
]


@app.command()
def main():
    """
    Upgrade knausj
    """

    repo_base_path.mkdir(parents=True, exist_ok=True)
    log_dir = repo_base_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    repo_path = repo_base_path / "knausj_staging"

    print("[bold green]Welcome to the upgrade-knausj script![/bold green] :wave:\n")
    print_slack_help_info("you run into any issues", True)
    print(f"Working in '{repo_path}'...\n")
    repo = Repo.init(repo_path)

    if repo.git.status("--porcelain") != "":
        error_and_exit(
            "Working directory has uncommitted changes; commit and try again"
        )

    mine_main, mine_remote_main = setup_mine(repo)
    knausj_main = setup_knausj(repo)

    mine_main.checkout(True)

    for challenging_commit in challenging_commits:
        handle_challenging_commit(repo, log_dir, challenging_commit, mine_main)

    if not repo.is_ancestor(knausj_main.commit, repo.head.commit):
        print("Merging with 'knausj_main'...")
        merge_exiting_on_conflict(
            repo,
            knausj_main.commit,
            f"Merge my {mine_remote_main.remote_head} branch with knausj main branch",
        )

    if mine_main.commit == mine_remote_main.commit:
        print(
            "[bold green]Looks like everything is already up to date![/bold green] :raised_hands:"
        )
        exit(0)

    if Confirm.ask(
        ":tada: [bold green]All done![/bold green] :tada:  Shall I push to your repo?"
    ):
        repo.git.push(
            mine_remote_main.remote_name, f"HEAD:{mine_remote_main.remote_head}"
        )
