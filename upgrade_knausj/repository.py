from pathlib import Path
from typing import Literal, Union

from git.remote import Remote
from git.repo import Repo

ORIGIN = "origin"
UPSTREAM = "upstream"

RemoteName = Literal["origin", "upstream"]


class Repository:
    path: Path
    _repo: Repo

    def __init__(self, path: Path):
        self.path = path

    def _parse_uri(self, uri: str) -> str:
        return uri

    @property
    def origin(self):
        return next(remote for remote in self._repo.remotes if remote.name == ORIGIN)

    def _get_remote(self, name: RemoteName) -> Remote:
        return next(remote for remote in self._repo.remotes if remote.name == name)

    def init(self):
        self._repo = Repo.init(self.path)

    def add_remote(self, name: RemoteName, raw_uri: str):
        uri = self._parse_uri(raw_uri)
        self._repo.create_remote(name, uri)

    def has_remote(self, name: RemoteName):
        return len([remote for remote in self._repo.remotes if remote.name == name]) > 0

    def fetch_remote(self, name: RemoteName):
        remote = self._get_remote(name)
        remote.fetch()
