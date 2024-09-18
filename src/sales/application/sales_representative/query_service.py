from abc import ABC, abstractmethod
from collections.abc import Iterable

from sales.application.sales_representative.query_model import (
    SalesRepresentativeReadModel,
)


class SalesRepresentativeQueryService(ABC):
    @abstractmethod
    def get(self, representative_id: str) -> SalesRepresentativeReadModel | None: ...

    @abstractmethod
    def get_all(self) -> Iterable[SalesRepresentativeReadModel]: ...
