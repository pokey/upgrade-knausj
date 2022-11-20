from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ConditionResult:
    success: bool
    message: str


class Condition(ABC):
    @abstractmethod
    def __call__(self) -> ConditionResult:
        pass
