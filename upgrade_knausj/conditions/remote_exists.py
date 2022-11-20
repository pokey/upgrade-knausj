from upgrade_knausj.repository import RemoteName, Repository
from upgrade_knausj.types.condition import Condition, ConditionResult


class RemoteExists(Condition):
    _repository: Repository
    _name: RemoteName

    def __init__(self, repository: Repository, name: RemoteName):
        self._repository = repository
        self._name = name

    def __call__(self) -> ConditionResult:
        return ConditionResult(
            self._repository.has_remote(self._name), f"Remote {self._name} should exist"
        )
