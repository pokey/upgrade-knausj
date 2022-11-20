from abc import abstractmethod
from typing import Callable

from upgrade_knausj.conditions.remote_exists import RemoteExists
from upgrade_knausj.conditions.repository_exists import RepositoryExists
from upgrade_knausj.repository import ORIGIN, UPSTREAM, RemoteName, Repository
from upgrade_knausj.types.step import Step


class AddRemote(Step):
    _repository: Repository
    _name: RemoteName

    @abstractmethod
    def _get_uri(self) -> str:
        pass

    def __init__(self, repository: Repository, name: RemoteName):
        self._repository = repository
        self._name = name

        self.precondition = RepositoryExists(repository)
        self.postcondition = RemoteExists(repository, name)

    def __call__(self) -> None:
        self._repository.add_remote(self._name, self._get_uri())


class AddOrigin(AddRemote):
    name = "Connect to your repository"
    _uri_getter: Callable[[], str]

    def __init__(self, repository: Repository, get_uri: Callable[[], str]):
        super().__init__(repository, ORIGIN)
        self._uri_getter = get_uri

    def _get_uri(self) -> str:
        return self._uri_getter()


class AddUpstream(AddRemote):
    name = "Connect to upstream knausj repository"
    _uri: str

    def __init__(self, repository: Repository, upstream_uri: str):
        super().__init__(repository, UPSTREAM)
        self._uri = upstream_uri

    def _get_uri(self) -> str:
        return self._uri
