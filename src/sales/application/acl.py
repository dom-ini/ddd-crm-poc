from abc import ABC, abstractmethod
from typing import Protocol, Self, TypeVar

CustomerT = TypeVar("CustomerT")


class CustomerRepository(Protocol):
    def get(self, customer_id: str) -> CustomerT | None: ...


class CustomerUnitOfWork(Protocol):
    repository: CustomerRepository

    def __enter__(self) -> Self: ...


class ICustomerService(ABC):
    def __init__(self, customer_uow: CustomerUnitOfWork) -> None:
        self.customer_uow = customer_uow

    @abstractmethod
    def customer_exists(self, customer_id: str) -> bool: ...


class CustomerService(ICustomerService):
    def customer_exists(self, customer_id: str) -> bool:
        with self.customer_uow as uow:
            return bool(uow.repository.get(customer_id))
