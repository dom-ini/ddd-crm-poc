from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import TypeVar

from building_blocks.application.query_model import BaseReadModel

ReadModelT = TypeVar("ReadModelT", bound=BaseReadModel)


class ValueObjectService(ABC):
    @abstractmethod
    def get_all(self) -> Iterable[ReadModelT]: ...
