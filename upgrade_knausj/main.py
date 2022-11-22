import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import typer
import yaml
from git.exc import GitCommandError
from git.objects.commit import Commit
from git.refs import Head
from git.repo import Repo
from rich import print
from rich.prompt import Confirm

from upgrade_knausj.cd import cd

app = typer.Typer()

repo_base_path = Path.home() / "knausj_staging"

# FIXME: Support http url
knausj_uri = "git@github.com:knausj85/knausj_talon.git"


@dataclass
class ChallengingCommit:
    sha: str
    is_precommit: bool


challenging_commits = [
    ChallengingCommit("2877a6849d75e5fa78c9453991a9235b4f6d9dcf", True),
    ChallengingCommit("3bf4882fa0a05b22171e59118bd7c9640aae753a", True),
    ChallengingCommit("446ec764c9caa98973eacd7f792b6a087a1b635f", True),
    ChallengingCommit("b25bac46c6543d0ec5fe2b2d09596444cd903371", False),
]


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

    repo_base_path.mkdir(parents=True, exist_ok=True)
    log_path = repo_base_path / "log.txt"
    repo_path = repo_base_path / "repo"

    print(f"Working in '{repo_path}'...\n")
    repo = Repo.init(repo_path)

    if repo.git.status("--porcelain") != "":
        error_and_exit(
            "Working directory has uncommitted changes; commit and try again"
        )

    mine, mine_main, mine_remote_main = setup_mine(repo, my_repo_uri, my_branch)
    knausj, knausj_main = setup_knausj(repo)

    mine_main.checkout()

    for challenging_commit in challenging_commits:
        handle_challenging_commit(repo, log_path, challenging_commit, mine_main)

    if not repo.is_ancestor(knausj_main.commit, repo.head.commit):
        print("Merging with knausj_main...")
        try:
            repo.git.merge(knausj_main)
        except GitCommandError as err:
            print(err.stdout)
            exit(1)

    if mine_main.commit == mine_remote_main.commit:
        print("Nothing to be done.")
        exit(0)

    if Confirm.ask(
        ":tada: [bold green]All done![/bold green] :tada:  Shall I push to your repo?"
    ):
        mine.push()


def setup_mine(repo: Repo, my_repo_uri: str, my_branch: str):
    if "mine" not in repo.remotes:
        mine = repo.create_remote("mine", my_repo_uri)
        print(f"\nCreated remote '{mine.name}' for '{my_repo_uri}'")
    else:
        mine = repo.remotes.mine

    mine.fetch()

    try:
        mine_remote_main = mine.refs[my_branch]
    except IndexError:
        error_and_exit(
            f"Branch '{my_branch}' does not exist on your repo\n"
            "Run with '--my-repo-uri' arg to specify your branch name (probably 'master')"
        )

    if "mine_main" not in repo.heads:
        mine_main = repo.create_head("mine_main", mine_remote_main)
        print(f"Created branch '{mine_main.name}' to track '{mine.name}:{my_branch}'")
        mine_main.set_tracking_branch(mine_remote_main)
    else:
        mine_main = repo.heads.mine_main

        if mine_main.commit != mine_remote_main.commit and not repo.is_ancestor(
            mine_remote_main.commit, mine_main.commit
        ):
            print(f"Local branch '{mine_main}' is outdated; updating...")
            mine.pull()

    return mine, mine_main, mine_remote_main


def setup_knausj(repo: Repo):
    if "knausj" not in repo.remotes:
        knausj = repo.create_remote("knausj", knausj_uri)
        print(f"\nCreated remote '{knausj.name}' for '{knausj_uri}'")
    else:
        knausj = repo.remotes.knausj

    knausj.fetch()

    knausj_remote_main = knausj.refs.main

    if "knausj_main" not in repo.heads:
        knausj_main = repo.create_head("knausj_main", knausj_remote_main)
        print(f"Created branch '{knausj_main.name}' to track '{knausj.name}:main'")
        knausj_main.set_tracking_branch(knausj_remote_main)
    else:
        knausj_main = repo.heads.knausj_main

        if knausj_main.commit != knausj_remote_main.commit and repo.is_ancestor(
            knausj_main.commit, knausj_remote_main.commit
        ):
            print(f"Local branch '{knausj_main}' is outdated; updating...")
            knausj.pull()

    return knausj, knausj_main


def error_and_exit(message: str):
    print(f":x: [bold red]Error[/bold red] {message}")
    sys.exit(1)


def handle_challenging_commit(
    repo: Repo, log_path: Path, challenging_commit: ChallengingCommit, mine_main: Head
):
    sha = challenging_commit.sha
    short_name = sha[:7]
    commit = repo.commit(sha)
    parent = commit.parents[0]

    if repo.is_ancestor(commit, repo.head.commit):
        return

    print(
        f"\nAssisting with challenging commit '{short_name}' (\"{commit.message.splitlines()[0]}\")"
    )

    if not repo.is_ancestor(parent, repo.head.commit):
        print(f"Merging with parent commit '{str(parent)[:7]}'")
        try:
            repo.git.merge(parent)
        except GitCommandError as err:
            print(err.stdout)
            exit(1)

    if not challenging_commit.is_precommit:
        print(f"Merging with commit '{short_name}'")
        try:
            repo.git.merge(commit)
        except GitCommandError as err:
            print(err.stdout)
            exit(1)
        return

    # Handle pre-commit commits; we just run pre-commit ourselves instead of
    # actually doing a merge
    tmp_branch = repo.create_head(f"merge_{short_name}", "HEAD")
    tmp_branch.checkout()
    print(f"Created temp branch '{tmp_branch.name}'")
    print(f"Copying pre-commit config from '{short_name}'...")

    repo.git.checkout(commit, ".pre-commit-config.yaml")

    if sha.startswith("3bf4882"):
        print("Force shed version to 0.10.3 to work around bug...")
        pre_commit_config = Path(repo.working_tree_dir) / ".pre-commit-config.yaml"  # type: ignore
        with open(pre_commit_config) as f:
            config = yaml.safe_load(f)
        config["repos"][-1]["rev"] = "0.10.3"
        with open(pre_commit_config, "w") as f:
            yaml.dump(config, f)

    print("Running pre-commit...")
    with cd(repo.working_tree_dir), open(log_path, "a") as out:
        result = subprocess.run(["pre-commit", "run", "--all"], stdout=out, stderr=out)

    if result.returncode not in [0, 1]:
        print(f"Error running pre-commit; see '{log_path}' for more info")
        sys.exit(result.returncode)

    if sha.startswith("3bf4882"):
        repo.git.restore(str(pre_commit_config))

    repo.git.add(all=True)

    if len(repo.index.entries) > 0:
        repo.index.commit(message="Run pre-commit")

    print("Initiating merge...")
    mine_main.checkout()

    merge_commit = Commit.create_from_tree(
        repo,
        tmp_branch.commit.tree,
        f"Merge my main with {sha[:7]} by running pre-commit",
        [mine_main.commit, commit],
    )
    mine_main.commit = merge_commit
    mine_main.checkout(True)
