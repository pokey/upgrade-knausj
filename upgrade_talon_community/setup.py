from git import Remote
from git.repo import Repo
from rich import print
from rich.prompt import Prompt

# FIXME: Support ssh url
community_uri = "https://github.com/talonhub/community.git"
mine_remote_name = "mine"
community_remote_name = "community"
mine_main_local_name = "mine_main"
community_main_local_name = "community_main"


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
        remote_uri = Prompt.ask("Enter the git URI for your fork of community")
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


def setup_community(repo: Repo):
    if community_remote_name not in repo.remotes:
        community = repo.create_remote(community_remote_name, community_uri)
        print(f"\nCreated remote '{community.name}' for '{community_uri}'")
    else:
        community = repo.remotes.community

    community.fetch()

    community_remote_main = community.refs.main

    if community_main_local_name not in repo.heads:
        community_main = repo.create_head(
            community_main_local_name, community_remote_main
        )
        print(
            f"Created branch '{community_main.name}' to track '{community.name}:main'"
        )
        community_main.set_tracking_branch(community_remote_main)
    else:
        community_main = repo.heads.community_main

        if community_main.commit != community_remote_main.commit and repo.is_ancestor(
            community_main.commit, community_remote_main.commit
        ):
            print(f"Local branch '{community_main}' is outdated; updating...")
            community_main.commit = community_remote_main.commit

    return community_main
