from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ConditionResult:
    success: bool
    message: str


class Step(ABC):
    name: str

    @abstractmethod
    def precondition(self) -> ConditionResult:
        pass

    @abstractmethod
    def postcondition(self) -> ConditionResult:
        pass

    @abstractmethod
    def run(self) -> None:
        pass
