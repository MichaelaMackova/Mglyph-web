from abc import ABC, abstractmethod
from sqlalchemy import Select


class RepositoryInterface(ABC):
    class LoadOptionsInterface(ABC):
        @abstractmethod
        def add_options_to_statement(self, statement: Select) -> Select:
            pass

        @staticmethod
        @abstractmethod
        def all_options() -> "RepositoryInterface.LoadOptionsInterface":
            pass