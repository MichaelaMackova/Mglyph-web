from abc import ABC, abstractmethod
from typing import TypeVar

# Declare type variable
T = TypeVar('T') 


class RepositoryInterface(ABC):
    class LoadOptionsInterface(ABC):
        @abstractmethod
        def add_options_to_statement(self, statement: T) -> T:
            pass

        @staticmethod
        @abstractmethod
        def all_options() -> "RepositoryInterface.LoadOptionsInterface":
            pass