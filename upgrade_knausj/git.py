from git.exc import GitCommandError
from git.objects.commit import Commit
from git.repo import Repo
from rich import print

from upgrade_knausj.util import print_slack_help_info


def merge_exiting_on_conflict(repo: Repo, commit: Commit):
    try:
        repo.git.merge(commit)
    except GitCommandError as err:
        print(err.stdout)
        print(
            f"[bold yellow]Please resolve any merge conflicts in [green]{repo.working_tree_dir}[/green], commit your changes, and re-run upgrade-knausj[/bold yellow]\n"
        )
        print_slack_help_info("you aren't sure how to resolve a conflict")
        exit(1)
