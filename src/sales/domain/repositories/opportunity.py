from abc import ABC, abstractmethod
from collections.abc import Sequence

from sales.domain.entities.opportunity import Opportunity


class OpportunityRepository(ABC):
    @abstractmethod
    def get(self, opportunity_id: str) -> Opportunity | None: ...

    @abstractmethod
    def get_all_by_customer(self, customer_id: str) -> Sequence[Opportunity]: ...

    @abstractmethod
    def create(self, opportunity: Opportunity) -> None: ...

    @abstractmethod
    def update(self, opportunity: Opportunity) -> None: ...
