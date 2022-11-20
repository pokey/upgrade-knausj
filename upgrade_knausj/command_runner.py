from abc import ABC, abstractmethod


class CommandRunner(ABC):
    @abstractmethod
    def __call__(self) -> None:
        pass
