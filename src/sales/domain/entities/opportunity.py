from typing import Self
from uuid import UUID
from attrs import define, field
import datetime as dt

from building_blocks.domain.entity import AggregateRoot
from building_blocks.domain.utils.date import get_current_timestamp
from sales.domain.entities.notes import Notes, NotesHistory
from sales.domain.exceptions import OnlyOwnerCanEditNotes
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.note import Note
from sales.domain.value_objects.offer_item import OfferItem
from sales.domain.value_objects.opportunity_stage import OpportunityStage
from sales.domain.value_objects.priority import Priority

Offer = tuple[OfferItem, ...]


@define(eq=False, kw_only=True)
class Opportunity(AggregateRoot):
    source: AcquisitionSource
    stage: OpportunityStage
    priority: Priority
    _created_by_id: UUID = field(alias="created_by_id")
    _customer_id: UUID = field(alias="customer_id")
    _owner_id: UUID = field(alias="owner_id")
    _created_at: dt.datetime = field(init=False, factory=get_current_timestamp)
    _offer: Offer = field(alias="offer")
    _notes: Notes = field(init=False)

    @classmethod
    def make(
        cls,
        *,
        id: UUID,
        created_by_id: UUID,
        customer_id: UUID,
        owner_id: UUID,
        source: AcquisitionSource,
        stage: OpportunityStage,
        priority: Priority,
        offer: Offer,
    ) -> Self:
        notes = Notes()
        opportunity = cls(
            id=id,
            created_by_id=created_by_id,
            customer_id=customer_id,
            owner_id=owner_id,
            source=source,
            stage=stage,
            priority=priority,
            offer=offer,
        )
        opportunity._notes = notes
        return opportunity

    @classmethod
    def reconstitute(
        cls,
        *,
        id: UUID,
        created_by_id: UUID,
        customer_id: UUID,
        owner_id: UUID,
        created_at: dt.datetime,
        source: AcquisitionSource,
        stage: OpportunityStage,
        priority: Priority,
        offer: Offer,
        notes: Notes,
    ):
        opportunity = cls(
            id=id,
            created_by_id=created_by_id,
            customer_id=customer_id,
            owner_id=owner_id,
            source=source,
            stage=stage,
            priority=priority,
            offer=offer,
        )
        opportunity._notes = notes
        opportunity._created_at = created_at
        return opportunity

    @property
    def created_at(self) -> dt.datetime:
        return self._created_at

    @property
    def offer(self) -> Offer:
        return self._offer

    @property
    def customer_id(self) -> UUID:
        return self._customer_id

    @property
    def owner_id(self) -> UUID:
        return self._owner_id

    @property
    def note(self) -> Note | None:
        return self._notes.most_recent

    @property
    def notes_history(self) -> NotesHistory:
        return self._notes.history

    def change_note(self, new_content: str, editor_id: UUID) -> Self:
        if not editor_id == self.owner_id:
            raise OnlyOwnerCanEditNotes
        self._notes.change_note(new_content=new_content, editor_id=editor_id)
        return self

    def modify_offer(self, new_offer: Offer) -> Self:
        self._offer = new_offer
        return self

    def __str__(self) -> str:
        return f"Opportunity: stage={self.stage}, priority={self.priority}"
