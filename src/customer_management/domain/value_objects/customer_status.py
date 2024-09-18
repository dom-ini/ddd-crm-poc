from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol, Self, Tuple
from attrs import define, field
from customer_management.domain.exceptions import (
    CannotConvertArchivedCustomer,
    CustomerAlreadyArchived,
    CustomerAlreadyConverted,
)

ContactPersons = Tuple


class CustomerStatusName(str, Enum):
    INITIAL = "initial"
    CONVERTED = "converted"
    ARCHIVED = "archived"


class Customer(Protocol):
    contact_persons: ContactPersons

    def _validate_contact_persons_called_by_status(
        self, contact_persons: ContactPersons
    ) -> None: ...
    def _change_status(self, status: "CustomerStatus") -> None: ...


class CustomerStatus(ABC):
    name: str
    customer: Customer

    @abstractmethod
    def convert(self) -> None:
        pass

    @abstractmethod
    def archive(self) -> None:
        pass

    @property
    @abstractmethod
    def should_validate_contact_persons(self) -> bool:
        pass

    def __str__(self) -> str:
        status_name = self.__class__.__name__.lower().rstrip("status")
        return f"status={status_name}"


@define(frozen=True)
class InitialStatus(CustomerStatus):
    name: str = field(init=False, default=CustomerStatusName.INITIAL)
    customer: Customer

    def convert(self) -> None:
        self.customer._validate_contact_persons_called_by_status(
            self.customer.contact_persons
        )
        self.customer._change_status(ConvertedStatus(self.customer))

    def archive(self) -> None:
        self.customer._change_status(ArchivedStatus(self.customer))

    @property
    def should_validate_contact_persons(self) -> bool:
        return False


@define(frozen=True)
class ConvertedStatus(CustomerStatus):
    name: str = field(init=False, default=CustomerStatusName.CONVERTED)
    customer: Customer

    def convert(self) -> None:
        raise CustomerAlreadyConverted

    def archive(self) -> None:
        self.customer._change_status(ArchivedStatus(self.customer))

    @property
    def should_validate_contact_persons(self) -> bool:
        return True


@define(frozen=True)
class ArchivedStatus(CustomerStatus):
    name: str = field(init=False, default=CustomerStatusName.ARCHIVED)
    customer: Customer

    def convert(self) -> None:
        raise CannotConvertArchivedCustomer

    def archive(self) -> None:
        raise CustomerAlreadyArchived

    @property
    def should_validate_contact_persons(self) -> bool:
        return False
