from abc import ABC, abstractmethod
from typing import Protocol, Self

from building_blocks.application.exceptions import ObjectDoesNotExist


class Customer(Protocol):
    status: str


class CustomerRepository(Protocol):
    def get(self, customer_id: str) -> Customer | None: ...


class CustomerUnitOfWork(Protocol):
    repository: CustomerRepository

    def __enter__(self) -> Self: ...


class ICustomerService(ABC):
    def __init__(self, customer_uow: CustomerUnitOfWork) -> None:
        self.customer_uow = customer_uow

    @abstractmethod
    def customer_exists(self, customer_id: str) -> bool: ...

    @abstractmethod
    def get_customer_status(self, customer_id: str) -> str: ...


class CustomerService(ICustomerService):
    def customer_exists(self, customer_id: str) -> bool:
        with self.customer_uow as uow:
            return bool(uow.repository.get(customer_id))

    def get_customer_status(self, customer_id: str) -> str:
        with self.customer_uow as uow:
            customer = uow.repository.get(customer_id)
        if customer is None:
            raise ObjectDoesNotExist(customer_id)
        return customer.status
