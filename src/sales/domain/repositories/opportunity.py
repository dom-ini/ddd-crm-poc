from abc import ABC, abstractmethod

from sales.domain.entities.opportunity import Opportunity


class OpportunityRepository(ABC):
    @abstractmethod
    def get(self, opportunity_id: str) -> Opportunity | None: ...

    @abstractmethod
    def create(self, opportunity: Opportunity) -> None: ...

    @abstractmethod
    def update(self, opportunity: Opportunity) -> None: ...
