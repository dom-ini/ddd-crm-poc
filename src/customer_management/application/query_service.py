from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence

from building_blocks.application.filters import FilterCondition
from customer_management.application.query_model import ContactPersonReadModel, CustomerReadModel


class CustomerQueryService(ABC):
    @abstractmethod
    def get(self, customer_id: str) -> CustomerReadModel | None: ...

    @abstractmethod
    def get_all(self) -> Sequence[CustomerReadModel]: ...

    @abstractmethod
    def get_filtered(self, filters: Iterable[FilterCondition]) -> Sequence[CustomerReadModel]: ...

    @abstractmethod
    def get_contact_persons(self, customer_id: str) -> Sequence[ContactPersonReadModel] | None: ...
