from git.exc import GitCommandError
from git.objects.commit import Commit
from git.repo import Repo


def merge_exiting_on_conflict(repo: Repo, commit: Commit):
    try:
        repo.git.merge(commit)
    except GitCommandError as err:
        print(err.stdout)
        exit(1)
