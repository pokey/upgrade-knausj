from pathlib import Path

from git.repo import Repo

from upgrade_knausj.step import ConditionResult, Step


class InitializeRepo(Step):
    _repo_path: Path

    def __init__(self, repo_path):
        self.name = "Initialize repository"
        self._repo_path = repo_path

    def precondition(self) -> ConditionResult:
        return ConditionResult(True, "")

    def postcondition(self) -> ConditionResult:
        return ConditionResult(self._repo_path.exists(), "Repository should exist")

    def run(self) -> None:
        Repo.init(self._repo_path)
