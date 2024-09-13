from abc import ABC, abstractmethod

from sales.domain.entities.lead import Lead


class LeadRepository(ABC):
    @abstractmethod
    def get(self, lead_id: str) -> Lead | None: ...

    @abstractmethod
    def create(self, lead: Lead) -> None: ...

    @abstractmethod
    def update(self, lead: Lead) -> None: ...
