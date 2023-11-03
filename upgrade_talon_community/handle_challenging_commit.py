import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml
from git.objects.commit import Commit
from git.refs import Head
from git.repo import Repo
from rich import print
from upgrade_talon_community.git import merge_exiting_on_conflict
from upgrade_talon_community.util import cd, print_error, print_slack_help_info


@dataclass
class ChallengingCommit:
    sha: str
    is_precommit: bool
    needs_patch: bool = False


def handle_challenging_commit(
    repo: Repo, log_dir: Path, challenging_commit: ChallengingCommit, mine_main: Head
):
    sha = challenging_commit.sha
    short_name = sha[:7]
    commit = repo.commit(sha)
    parent = commit.parents[0]
    main_remote_branch_name: str = (
        mine_main.tracking_branch().remote_head  # pyright: ignore [reportOptionalMemberAccess]
    )

    if repo.is_ancestor(commit, repo.head.commit):
        return

    print(
        f"\nAssisting with challenging commit '{short_name}' (\"{commit.message.splitlines()[0]}\")"
    )

    if not repo.is_ancestor(parent, repo.head.commit):
        parent_short_name = str(parent)[:7]
        print(f"Merging with parent commit '{parent_short_name}'")
        merge_exiting_on_conflict(
            repo,
            parent,
            f"Merge my {main_remote_branch_name} branch with community {parent_short_name}",
        )

    if challenging_commit.is_precommit:
        perform_pre_commit_merge(
            repo, log_dir, commit, mine_main, challenging_commit.needs_patch
        )
    else:
        print(f"Merging with commit '{short_name}'")
        merge_exiting_on_conflict(
            repo,
            commit,
            f"Merge my {main_remote_branch_name} branch with community {short_name}",
        )


def perform_pre_commit_merge(
    repo: Repo, log_dir: Path, commit: Commit, mine_main: Head, needs_patch: bool
):
    sha = commit.hexsha
    short_name = sha[:7]
    main_remote_branch_name: str = (
        mine_main.tracking_branch().remote_head  # pyright: ignore [reportOptionalMemberAccess]
    )

    # Handle pre-commit commits; we just run pre-commit ourselves instead of
    # actually doing a merge
    tmp_branch = repo.create_head(f"merge-{short_name}")
    tmp_branch.checkout()
    print(f"Created temp branch '{tmp_branch.name}'")
    print(f"Copying pre-commit config from '{short_name}'...")

    repo.git.checkout(commit, ".pre-commit-config.yaml")

    if not sha.startswith("2877a68"):
        repo.git.checkout(commit, ".editorconfig")

    add_and_commit_any_changes(repo, f"Take pre-commit config from {short_name}")

    if needs_patch:
        pre_commit_config = Path(repo.working_tree_dir) / ".pre-commit-config.yaml"  # type: ignore
        with open(pre_commit_config) as f:
            config = yaml.safe_load(f)
        if sha.startswith("3bf4882"):
            # For some reason shed before 0.10.7 doesn't work anymore, so we just
            # force the newer version
            print("Force shed version to 0.10.7 to work around bug...")
            config["repos"][-1]["rev"] = "0.10.7"
        if sha.startswith("446ec76"):
            # Talonfmt before 1.8.1 had issues, so we just force the newer
            # version
            print("Force talonfmt version to 1.8.1 to work around bug...")
            config["repos"][-1]["rev"] = "1.8.1"
        if sha.startswith("446ec76") or sha.startswith("4612817"):
            print(
                "Temporarily disable some formatters due to legacy ones having problems..."
            )
            config["repos"][2:5] = []
        with open(pre_commit_config, "w") as f:
            yaml.dump(config, f)

        add_and_commit_any_changes(repo, "Modify pre-commit config to work around bugs")

    print("Running pre-commit...")
    log_path = log_dir / f"pre-commit-{short_name}.txt"
    with cd(repo.working_tree_dir), open(log_path, "w") as out:
        result = subprocess.run(
            ["pre-commit", "run", "--all", "--verbose"], stdout=out, stderr=out
        )

    if result.returncode not in [0, 1]:
        print("")
        print_error(f"running pre-commit; see '{log_path}' for more info")
        print_slack_help_info("you get stuck")

        counter = 1
        error_branch_name = f"pre-commit-{short_name}-error"
        while error_branch_name in repo.heads:
            counter += 1
            error_branch_name = f"pre-commit-{short_name}-error-{counter}"

        error_branch = repo.create_head(error_branch_name)
        error_branch.checkout()
        repo.delete_head(tmp_branch)
        add_and_commit_any_changes(repo, "Failed attempt to run pre-commit")
        sys.exit(result.returncode)

    add_and_commit_any_changes(repo, "Run pre-commit")

    if needs_patch:
        repo.git.restore(str(pre_commit_config))  # type: ignore
        repo.git.checkout(commit, ".pre-commit-config.yaml")
        add_and_commit_any_changes(repo, f"Reset pre-commit config to {short_name}")

    print("Initiating merge...")
    mine_main.checkout()

    # Manually construct a merge commit, using `mine_main` and the community
    # pre-commit commit as parents, and using the tree we constructed by running
    # pre-commit on `mine_main` using the pre-commit config from the community
    # pre-commit commit
    merge_commit = Commit.create_from_tree(
        repo,
        tmp_branch.commit.tree,
        f"Merge my {main_remote_branch_name} branch with community {short_name} by running pre-commit",
        [mine_main.commit, commit],
    )
    mine_main.commit = merge_commit
    mine_main.checkout(True)


def add_and_commit_any_changes(repo: Repo, message: str):
    repo.git.add(all=True)

    if len(repo.index.entries) > 0:
        repo.index.commit(message=message)
