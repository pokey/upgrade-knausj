from pathlib import Path
from typing import Literal, Union

from git.repo import Repo

ORIGIN = "origin"
UPSTREAM = "upstream"

RemoteName = Union[Literal["origin"], Literal["upstream"]]


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

    def init(self):
        self._repo = Repo.init(self.path)

    def add_remote(self, name: RemoteName, raw_uri: str):
        uri = self._parse_uri(raw_uri)
        self._repo.create_remote(name, uri)

    def has_remote(self, name: RemoteName):
        return len([remote for remote in self._repo.remotes if remote.name == name]) > 0
