from abc import ABC, abstractmethod
from typing import Iterable

from building_blocks.application.filters import FilterCondition
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.notes.query_model import NoteReadModel


class LeadQueryService(ABC):
    @abstractmethod
    def get(self, lead_id: str) -> LeadReadModel | None: ...

    @abstractmethod
    def get_all(self) -> Iterable[LeadReadModel]: ...

    @abstractmethod
    def get_filtered(
        self, filters: Iterable[FilterCondition]
    ) -> Iterable[LeadReadModel]: ...

    @abstractmethod
    def get_notes(self, lead_id: str) -> Iterable[NoteReadModel] | None: ...

    @abstractmethod
    def get_assignment_history(
        self, lead_id: str
    ) -> Iterable[AssignmentReadModel] | None: ...
