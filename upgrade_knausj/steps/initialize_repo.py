from upgrade_knausj.conditions.always_true import AlwaysTrue
from upgrade_knausj.conditions.repository_exists import RepositoryExists
from upgrade_knausj.repository import Repository
from upgrade_knausj.types.step import Step


class InitializeRepo(Step):
    name = "Initialize repository"
    always_run: bool = True

    _repository: Repository

    def __init__(self, repository: Repository):
        self._repository = repository

        self.precondition = AlwaysTrue()
        self.postcondition = RepositoryExists(repository)

    def __call__(self) -> None:
        self._repository.init()
