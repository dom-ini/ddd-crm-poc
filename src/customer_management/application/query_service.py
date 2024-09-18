from abc import ABC, abstractmethod
from collections.abc import Iterable

from building_blocks.application.filters import FilterCondition
from customer_management.application.query_model import (
    ContactPersonReadModel,
    CustomerReadModel,
)


class CustomerQueryService(ABC):
    @abstractmethod
    def get(self, customer_id: str) -> CustomerReadModel | None: ...

    @abstractmethod
    def get_all(self) -> Iterable[CustomerReadModel]: ...

    @abstractmethod
    def get_filtered(
        self, filters: Iterable[FilterCondition]
    ) -> Iterable[CustomerReadModel]: ...

    @abstractmethod
    def get_contact_persons(
        self, customer_id: str
    ) -> Iterable[ContactPersonReadModel] | None: ...
