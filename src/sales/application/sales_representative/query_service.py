from abc import ABC, abstractmethod
from collections.abc import Sequence

from sales.application.sales_representative.query_model import SalesRepresentativeReadModel


class SalesRepresentativeQueryService(ABC):
    @abstractmethod
    def get(self, representative_id: str) -> SalesRepresentativeReadModel | None: ...

    @abstractmethod
    def get_all(self) -> Sequence[SalesRepresentativeReadModel]: ...
