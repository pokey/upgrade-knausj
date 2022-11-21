from abc import abstractmethod
from typing import Callable

from upgrade_knausj.conditions.always_true import AlwaysTrue
from upgrade_knausj.conditions.compound_condition import CompoundCondition
from upgrade_knausj.conditions.remote_exists import RemoteExists
from upgrade_knausj.conditions.repository_exists import RepositoryExists
from upgrade_knausj.repository import ORIGIN, UPSTREAM, RemoteName, Repository
from upgrade_knausj.types.step import Step


class FetchRemote(Step):
    always_run: bool = True

    _repository: Repository
    _name: RemoteName

    def __init__(self, repository: Repository, name: RemoteName):
        self._repository = repository
        self._name = name

        self.precondition = CompoundCondition(
            RepositoryExists(repository), RemoteExists(repository, name)
        )
        self.postcondition = AlwaysTrue()

    def __call__(self) -> None:
        self._repository.fetch_remote(self._name)


class FetchOrigin(FetchRemote):
    name = "Fetch from your repository"

    def __init__(self, repository: Repository):
        super().__init__(repository, ORIGIN)


class FetchUpstream(FetchRemote):
    name = "Fetch from upstream knausj repository"

    def __init__(self, repository: Repository):
        super().__init__(repository, UPSTREAM)
