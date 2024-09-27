from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Iterable

from building_blocks.application.filters import FilterCondition
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.notes.query_model import NoteReadModel


class LeadQueryService(ABC):
    @abstractmethod
    def get(self, lead_id: str) -> LeadReadModel | None: ...

    @abstractmethod
    def get_all(self) -> Sequence[LeadReadModel]: ...

    @abstractmethod
    def get_filtered(self, filters: Iterable[FilterCondition]) -> Sequence[LeadReadModel]: ...

    @abstractmethod
    def get_notes(self, lead_id: str) -> Sequence[NoteReadModel] | None: ...

    @abstractmethod
    def get_assignment_history(self, lead_id: str) -> Sequence[AssignmentReadModel] | None: ...
