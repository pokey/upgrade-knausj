from git.repo import Repo

from upgrade_knausj.util import error_and_exit

# FIXME: Support http url
knausj_uri = "git@github.com:knausj85/knausj_talon.git"


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
