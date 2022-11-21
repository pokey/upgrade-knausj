import subprocess
import sys
import time
from pathlib import Path

import typer
from git.repo import Repo
from rich import print

from upgrade_knausj.cd import cd

app = typer.Typer()

repo_base_path = Path.home() / "knausj_staging"

# FIXME: Support http url
knausj_uri = "git@github.com:knausj85/knausj_talon.git"


@app.command()
def main(
    my_repo_uri: str = typer.Option(
        ..., prompt=True, help="The git URI for your fork of knausj"
    ),
    my_branch: str = typer.Option("main", help="Which branch to use"),
):
    """
    Upgrade knausj
    """

    name = time.strftime("%Y-%m-%dT%H-%M-%S")

    repo_base_path.mkdir(parents=True, exist_ok=True)
    log_dir = repo_base_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{name}.txt"
    repo_path = repo_base_path / name

    print(f"Logging to '{log_path}'\n")

    print(f"Initializing repo in '{repo_path}'...")
    repo = Repo.init(repo_path)

    mine = repo.create_remote("mine", my_repo_uri)
    print(f"\nCreated remote '{mine.name}' for '{my_repo_uri}'")
    mine.fetch()
    try:
        mine_remote_main = mine.refs[my_branch]
    except IndexError:
        print(
            f":x: [bold red]Error[/bold red] Branch '{my_branch}' does not exist on your repo"
        )
        print(
            "Run with '--my-repo-uri' arg to specify your branch name (probably 'master')"
        )
        exit(1)
    mine_main = repo.create_head("mine_main", mine_remote_main)
    print(f"Created branch '{mine_main.name}' to track '{mine.name}:{my_branch}'")

    mine_main.set_tracking_branch(mine_remote_main)

    knausj = repo.create_remote("knausj", knausj_uri)
    print(f"\nCreated remote '{knausj.name}' for '{knausj_uri}'")
    knausj.fetch()
    knausj_remote_main = knausj.refs.main
    knausj_main = repo.create_head("knausj_main", knausj.refs.main)
    print(f"Created branch '{knausj_main.name}' to track '{knausj.name}:main'")
    knausj_main.set_tracking_branch(knausj_remote_main)

    mine_main.checkout()

    print("\nCopying pre-commit config from 'knausj'...")
    repo.git.checkout(knausj_main, ".pre-commit-config.yaml")

    if len(repo.index.entries) > 0:
        repo.index.commit(message="Get pre-commit from knausj")

    print("Running pre-commit...")
    with cd(repo_path), open(log_path, "a") as out:
        result = subprocess.run(["pre-commit", "run", "--all"], stdout=out, stderr=out)

    if result.returncode not in [0, 1]:
        print(f"Error running pre-commit; see {log_path} for more info")
        sys.exit(result.returncode)

    repo.git.add(all=True)

    if len(repo.index.entries) > 0:
        repo.index.commit(message="Run pre-commit")

    print("Initiating merge...")
    repo.git.merge(knausj_main)
