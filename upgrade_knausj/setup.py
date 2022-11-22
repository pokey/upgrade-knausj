from git import Remote
from git.repo import Repo
from rich import print
from rich.prompt import Prompt

# FIXME: Support ssh url
knausj_uri = "https://github.com/knausj85/knausj_talon.git"
mine_remote_name = "mine"
knausj_remote_name = "knausj"
mine_main_local_name = "mine_main"
knausj_main_local_name = "knausj_main"


def setup_mine(repo: Repo):
    mine = setup_mine_remote(repo)

    mine.fetch()

    mine_main, mine_remote_main = setup_mine_main_branch(repo, mine)

    if mine_main.commit != mine_remote_main.commit and not repo.is_ancestor(
        mine_remote_main.commit, mine_main.commit
    ):
        print(f"Local branch '{mine_main}' is outdated; updating...")
        mine_main.checkout(True)
        repo.git.pull()

    return mine_main, mine_remote_main


def setup_mine_remote(repo: Repo) -> Remote:
    if mine_remote_name not in repo.remotes:
        remote_uri = Prompt.ask("Enter the git URI for your fork of knausj")
        mine = repo.create_remote(mine_remote_name, remote_uri)
        print(f"\nCreated remote '{mine.name}' for '{remote_uri}'")
    else:
        mine = repo.remotes.mine

    return mine


def setup_mine_main_branch(repo: Repo, mine: Remote):
    if mine_main_local_name in repo.heads:
        mine_main = repo.heads.mine_main
        mine_remote_main = mine_main.tracking_branch()
    else:
        mine_main = repo.create_head(mine_main_local_name, mine.refs[0])
        print(f"Created branch '{mine_main.name}'")
        mine_remote_main = None

    default_branch_name = "main"
    while mine_remote_main is None:
        remote_branch_name = Prompt.ask(
            "Enter the name of your remote branch", default=default_branch_name
        )

        try:
            mine_remote_main = mine.refs[remote_branch_name]
        except IndexError:
            print(
                f"Branch '{remote_branch_name}' does not exist on your repo\n"
                "Maybe you meant 'master'?"
            )
            default_branch_name = "master"
            continue

        mine_main.commit = mine_remote_main.commit
        mine_main.set_tracking_branch(mine_remote_main)
        mine_main.checkout(True)
        print(
            f"Set branch '{mine_main.name}' to track '{mine.name}:{remote_branch_name}'"
        )

    return mine_main, mine_remote_main


def setup_knausj(repo: Repo):
    if knausj_remote_name not in repo.remotes:
        knausj = repo.create_remote(knausj_remote_name, knausj_uri)
        print(f"\nCreated remote '{knausj.name}' for '{knausj_uri}'")
    else:
        knausj = repo.remotes.knausj

    knausj.fetch()

    knausj_remote_main = knausj.refs.main

    if knausj_main_local_name not in repo.heads:
        knausj_main = repo.create_head(knausj_main_local_name, knausj_remote_main)
        print(f"Created branch '{knausj_main.name}' to track '{knausj.name}:main'")
        knausj_main.set_tracking_branch(knausj_remote_main)
    else:
        knausj_main = repo.heads.knausj_main

        if knausj_main.commit != knausj_remote_main.commit and repo.is_ancestor(
            knausj_main.commit, knausj_remote_main.commit
        ):
            print(f"Local branch '{knausj_main}' is outdated; updating...")
            knausj_main.commit = knausj_remote_main.commit

    return knausj_main
