from abc import ABC, abstractmethod

from customer_management.domain.entities.customer import Customer


class CustomerRepository(ABC):
    @abstractmethod
    def get(self, customer_id: str) -> Customer | None: ...

    @abstractmethod
    def create(self, customer: Customer) -> None: ...

    @abstractmethod
    def update(self, customer: Customer) -> None: ...
