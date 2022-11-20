from abc import ABC, abstractmethod

from upgrade_knausj.types.condition import Condition


class Step(ABC):
    name: str
    precondition: Condition
    postcondition: Condition
    always_run: bool = False

    @abstractmethod
    def __call__(self) -> None:
        pass
