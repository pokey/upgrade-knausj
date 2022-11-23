from git.exc import GitCommandError
from git.objects.commit import Commit
from git.repo import Repo
from rich import print


def merge_exiting_on_conflict(repo: Repo, commit: Commit):
    try:
        repo.git.merge(commit)
    except GitCommandError as err:
        print(err.stdout)
        print(
            "[bold yellow]Please resolve any merge conflicts, commit your changes, and re-run upgrade-knausj[/bold yellow]"
        )
        exit(1)
