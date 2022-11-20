from upgrade_knausj.repository import Repository
from upgrade_knausj.types.condition import Condition, ConditionResult


class RepositoryExists(Condition):
    _repository: Repository

    def __init__(self, repository: Repository):
        self._repository = repository

    def __call__(self) -> ConditionResult:
        return ConditionResult(
            self._repository.path.exists(), "Repository should exist"
        )
