from abc import ABC, abstractmethod

from sales.domain.entities.sales_representative import SalesRepresentative


class SalesRepresentativeRepository(ABC):
    @abstractmethod
    def get(self, representative_id: str) -> SalesRepresentative | None: ...

    @abstractmethod
    def create(self, representative: SalesRepresentative) -> None: ...

    @abstractmethod
    def update(self, representative: SalesRepresentative) -> None: ...
