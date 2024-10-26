from abc import ABC, abstractmethod
from collections.abc import Sequence
from types import TracebackType
from typing import Protocol, Self, TypeVar

SalesRepT = TypeVar("SalesRepT")


class SalesRepresentativeRepository(Protocol):
    def get(self, representative_id: str) -> SalesRepT | None: ...


class SalesRepresentativeUnitOfWork(Protocol):
    repository: SalesRepresentativeRepository

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...


class ISalesRepresentativeService(ABC):
    def __init__(self, salesman_uow: SalesRepresentativeUnitOfWork) -> None:
        self.salesman_uow = salesman_uow

    @abstractmethod
    def salesman_exists(self, salesman_id: str) -> bool: ...


class SalesRepresentativeService(ISalesRepresentativeService):
    def salesman_exists(self, salesman_id: str) -> bool:
        with self.salesman_uow as uow:
            return bool(uow.repository.get(salesman_id))


class Opportunity(Protocol):
    stage_name: str


class OpportunityRepository(Protocol):
    def get_all_by_customer(self, customer_id: str) -> Sequence[Opportunity]: ...


class OpportunityUnitOfWork(Protocol):
    repository: OpportunityRepository

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...


class IOpportunityService(ABC):
    def __init__(self, opportunity_uow: OpportunityUnitOfWork) -> None:
        self.opportunity_uow = opportunity_uow

    @abstractmethod
    def get_opportunities_by_customer(self, customer_id: str) -> Sequence[Opportunity]: ...


class OpportunityService(IOpportunityService):
    def get_opportunities_by_customer(self, customer_id: str) -> Sequence[Opportunity]:
        with self.opportunity_uow as uow:
            return uow.repository.get_all_by_customer(customer_id=customer_id)
