from abc import ABC, abstractmethod
from typing import Protocol, Self, TypeVar

SalesRepT = TypeVar("SalesRepT")


class SalesRepresentativeRepository(Protocol):
    def get(self, representative_id: str) -> SalesRepT | None: ...


class SalesRepresentativeUnitOfWork(Protocol):
    repository: SalesRepresentativeRepository

    def __enter__(self) -> Self: ...


class ISalesRepresentativeService(ABC):
    def __init__(self, salesman_uow: SalesRepresentativeUnitOfWork) -> None:
        self.salesman_uow = salesman_uow

    @abstractmethod
    def salesman_exists(self, salesman_id: str) -> bool: ...


class SalesRepresentativeService(ISalesRepresentativeService):
    def salesman_exists(self, salesman_id: str) -> bool:
        with self.salesman_uow as uow:
            return bool(uow.repository.get(salesman_id))
