from abc import ABC, abstractmethod
from uuid import UUID

from sales.domain.entities.lead import Lead


class LeadRepository(ABC):
    @abstractmethod
    def create(self, lead: Lead) -> Lead: ...

    @abstractmethod
    def get_by_id(self, lead_id: UUID) -> Lead: ...
