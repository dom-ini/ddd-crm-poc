from abc import ABC, abstractmethod

from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.notes.query_model import NoteReadModel


class LeadQueryService(ABC):
    @abstractmethod
    def get(self, lead_id: str) -> LeadReadModel | None: ...

    @abstractmethod
    def get_all(self) -> tuple[LeadReadModel]: ...

    @abstractmethod
    def get_by_customer_and_owner_id(
        self, customer_id: str | None, owner_id: str | None
    ) -> tuple[LeadReadModel, ...]: ...

    @abstractmethod
    def get_notes(self, lead_id: str) -> tuple[NoteReadModel, ...] | None: ...

    @abstractmethod
    def get_assignment_history(
        self, lead_id: str
    ) -> tuple[AssignmentReadModel, ...] | None: ...
