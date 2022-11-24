import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml
from git.objects.commit import Commit
from git.refs import Head
from git.repo import Repo
from rich import print

from upgrade_knausj.git import merge_exiting_on_conflict
from upgrade_knausj.util import cd


@dataclass
class ChallengingCommit:
    sha: str
    is_precommit: bool


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
        merge_exiting_on_conflict(repo, parent)

    if challenging_commit.is_precommit:
        perform_pre_commit_merge(repo, log_path, commit, mine_main)
    else:
        print(f"Merging with commit '{short_name}'")
        merge_exiting_on_conflict(repo, commit)


def perform_pre_commit_merge(
    repo: Repo, log_path: Path, commit: Commit, mine_main: Head
):
    sha = commit.hexsha
    short_name = sha[:7]

    # Handle pre-commit commits; we just run pre-commit ourselves instead of
    # actually doing a merge
    tmp_branch = repo.create_head(f"merge_{short_name}", "HEAD")
    tmp_branch.checkout()
    print(f"Created temp branch '{tmp_branch.name}'")
    print(f"Copying pre-commit config from '{short_name}'...")

    repo.git.checkout(commit, ".pre-commit-config.yaml")

    if not sha.startswith("2877a68"):
        repo.git.checkout(commit, ".editorconfig")

    if sha.startswith("3bf4882") or sha.startswith("446ec76"):
        pre_commit_config = Path(repo.working_tree_dir) / ".pre-commit-config.yaml"  # type: ignore
        with open(pre_commit_config) as f:
            config = yaml.safe_load(f)
        if sha.startswith("3bf4882"):
            # For some reason shed before 0.10.3 doesn't work anymore, so we just
            # force the newer version
            print("Force shed version to 0.10.3 to work around bug...")
            config["repos"][-1]["rev"] = "0.10.3"
        if sha.startswith("446ec76"):
            # Talonfmt before 1.8.1 had issues, so we just force the newer
            # version
            print("Force talonfmt version to 1.8.1 to work around bug...")
            config["repos"][-1]["rev"] = "1.8.1"
        with open(pre_commit_config, "w") as f:
            yaml.dump(config, f)

    print("Running pre-commit...")
    with cd(repo.working_tree_dir), open(log_path, "a") as out:
        result = subprocess.run(["pre-commit", "run", "--all"], stdout=out, stderr=out)

    if result.returncode not in [0, 1]:
        print(f"Error running pre-commit; see '{log_path}' for more info")
        sys.exit(result.returncode)

    if sha.startswith("3bf4882") or sha.startswith("446ec76"):
        repo.git.restore(str(pre_commit_config))  # type: ignore
        repo.git.checkout(commit, ".pre-commit-config.yaml")

    repo.git.add(all=True)

    if len(repo.index.entries) > 0:
        repo.index.commit(message="Run pre-commit")

    print("Initiating merge...")
    mine_main.checkout()

    # Manually construct a merge commit, using `mine_main` and the knausj
    # pre-commit commit as parents, and using the tree we constructed by running
    # pre-commit on `mine_main` using the pre-commit config from the knausj
    # pre-commit commit
    merge_commit = Commit.create_from_tree(
        repo,
        tmp_branch.commit.tree,
        f"Merge my main with {short_name} by running pre-commit",
        [mine_main.commit, commit],
    )
    mine_main.commit = merge_commit
    mine_main.checkout(True)
