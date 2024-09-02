from typing import Self
from uuid import UUID

from attrs import define, field
from sales.domain.entities.notes import Notes, NotesHistory
from sales.domain.exceptions import (
    UnauthorizedLeadOwnerChange,
    OnlyOwnerCanEditNotes,
)
from sales.domain.value_objects.contact_data import ContactData
from sales.domain.value_objects.lead_assignment import LeadAssignment
from sales.domain.value_objects.note import Note
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from building_blocks.domain.entity import AggregateRoot


LeadAssignmentHistory = tuple[LeadAssignment]


@define(eq=False, kw_only=True)
class Lead(AggregateRoot):
    contact_data: ContactData
    source: AcquisitionSource
    _customer_id: UUID = field(alias="customer_id")
    _created_by_salesman_id: UUID = field(alias="created_by_salesman_id")
    _assignment_history: LeadAssignmentHistory = field(init=False, factory=tuple)
    _notes: Notes = field(init=False)

    @classmethod
    def make(
        cls,
        *,
        id: UUID,
        customer_id: UUID,
        created_by_salesman_id: UUID,
        notes_id: UUID,
        contact_data: ContactData,
        source: AcquisitionSource,
    ) -> Self:
        notes = Notes(id=notes_id)
        lead = cls(
            id=id,
            contact_data=contact_data,
            source=source,
            customer_id=customer_id,
            created_by_salesman_id=created_by_salesman_id,
        )
        lead._notes = notes
        return lead

    @classmethod
    def reconstitute(
        cls,
        *,
        id: UUID,
        customer_id: UUID,
        created_by_salesman_id: UUID,
        contact_data: ContactData,
        source: AcquisitionSource,
        assignment_history: LeadAssignmentHistory,
        notes: Notes,
    ) -> Self:
        lead = cls(
            id=id,
            contact_data=contact_data,
            source=source,
            customer_id=customer_id,
            created_by_salesman_id=created_by_salesman_id,
        )
        lead._notes = notes
        lead._assignment_history = assignment_history
        return lead

    @property
    def note(self) -> Note | None:
        return self._notes.most_recent

    @property
    def notes_history(self) -> NotesHistory:
        return self._notes.history

    @property
    def assigned_salesman_id(self) -> UUID | None:
        if not len(self._assignment_history):
            return None
        return self._assignment_history[-1].current_owner_id

    @property
    def has_assigned_salesman(self) -> bool:
        return self.assigned_salesman_id is not None

    @property
    def assignment_history(self) -> LeadAssignmentHistory:
        return self._assignment_history

    @property
    def created_by_salesman_id(self) -> UUID:
        return self._created_by_salesman_id

    @property
    def customer_id(self) -> UUID:
        return self._customer_id

    def assign_salesman(self, new_salesman_id: UUID, requestor_id: UUID) -> Self:
        self._check_assignment_permissions(requestor_id)
        self._record_salesman_assignment(
            new_salesman_id=new_salesman_id, requestor_id=requestor_id
        )
        return self

    def change_note(self, new_content: str, editor_id: UUID) -> Self:
        if self.has_assigned_salesman and not editor_id == self.assigned_salesman_id:
            raise OnlyOwnerCanEditNotes
        self._notes.change_note(new_content=new_content, editor_id=editor_id)
        return self

    def _check_assignment_permissions(self, requestor_id: UUID) -> None:
        is_lead_owner = (
            self.has_assigned_salesman and self.assigned_salesman_id == requestor_id
        )
        if not is_lead_owner:
            raise UnauthorizedLeadOwnerChange

    def _record_salesman_assignment(
        self, new_salesman_id: UUID, requestor_id: UUID
    ) -> None:
        assigned_from = self.assigned_salesman_id
        assignment = LeadAssignment(
            previous_owner_id=assigned_from,
            current_owner_id=new_salesman_id,
            assigned_by_id=requestor_id,
        )
        self._assignment_history = self._assignment_history + (assignment,)

    def __str__(self) -> str:
        return f"Lead: {self.contact_data}"
