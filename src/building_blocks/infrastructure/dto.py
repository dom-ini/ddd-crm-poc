from abc import ABC, abstractmethod
from typing import Self


class BaseDTO[DomainModel, ReadModel](ABC):
    @abstractmethod
    def to_domain(self) -> DomainModel: ...

    @abstractmethod
    def to_read_model(self) -> ReadModel: ...

    @classmethod
    def from_domain(cls, entity: DomainModel) -> Self:
        raise NotImplementedError
