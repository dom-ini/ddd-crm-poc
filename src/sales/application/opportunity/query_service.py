from abc import ABC, abstractmethod
from collections.abc import Iterable

from building_blocks.application.filters import FilterCondition
from sales.application.notes.query_model import NoteReadModel
from sales.application.opportunity.query_model import (
    OfferItemReadModel,
    OpportunityReadModel,
)


class OpportunityQueryService(ABC):
    @abstractmethod
    def get(self, opportunity_id: str) -> OpportunityReadModel | None: ...

    @abstractmethod
    def get_all(self) -> Iterable[OpportunityReadModel]: ...

    @abstractmethod
    def get_filtered(
        self, filters: Iterable[FilterCondition]
    ) -> Iterable[OpportunityReadModel]: ...

    @abstractmethod
    def get_notes(self, opportunity_id: str) -> Iterable[NoteReadModel] | None: ...

    @abstractmethod
    def get_offer(self, opportunity_id: str) -> Iterable[OfferItemReadModel] | None: ...
