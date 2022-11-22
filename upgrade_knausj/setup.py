from git.repo import Repo

from upgrade_knausj.util import error_and_exit

# FIXME: Support ssh url
knausj_uri = "https://github.com/knausj85/knausj_talon.git"
mine_main_local_name = "mine_main"
knausj_main_local_name = "knausj_main"


def setup_mine(repo: Repo, remote_uri: str, remote_branch_name: str):
    if "mine" not in repo.remotes:
        mine = repo.create_remote("mine", remote_uri)
        print(f"\nCreated remote '{mine.name}' for '{remote_uri}'")
    else:
        mine = repo.remotes.mine

    mine.fetch()

    try:
        mine_remote_main = mine.refs[remote_branch_name]
    except IndexError:
        error_and_exit(
            f"Branch '{remote_branch_name}' does not exist on your repo\n"
            "Run with '--my-repo-uri' arg to specify your branch name (probably 'master')"
        )

    if mine_main_local_name not in repo.heads:
        mine_main = repo.create_head(mine_main_local_name, mine_remote_main)
        print(
            f"Created branch '{mine_main.name}' to track '{mine.name}:{remote_branch_name}'"
        )
        mine_main.set_tracking_branch(mine_remote_main)
    else:
        mine_main = repo.heads.mine_main

        if mine_main.commit != mine_remote_main.commit and not repo.is_ancestor(
            mine_remote_main.commit, mine_main.commit
        ):
            print(f"Local branch '{mine_main}' is outdated; updating...")
            mine_main.checkout(True)
            repo.git.pull()

    return mine_main, mine_remote_main


def setup_knausj(repo: Repo):
    if "knausj" not in repo.remotes:
        knausj = repo.create_remote("knausj", knausj_uri)
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
