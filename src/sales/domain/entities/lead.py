import datetime as dt
from typing import Self

from attrs import define, field

from building_blocks.domain.entity import AggregateRoot
from building_blocks.domain.utils.date import get_current_timestamp
from sales.domain.entities.lead_assignments import AssignmentHistory, LeadAssignments
from sales.domain.entities.notes import Notes, NotesHistory
from sales.domain.exceptions import OnlyOwnerCanEditNotes, UnauthorizedLeadOwnerChange
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.contact_data import ContactData
from sales.domain.value_objects.lead_assignment_entry import LeadAssignmentEntry
from sales.domain.value_objects.note import Note


@define(eq=False, kw_only=True)
class Lead(AggregateRoot):
    contact_data: ContactData
    source: AcquisitionSource
    _customer_id: str = field(alias="customer_id")
    _created_by_salesman_id: str = field(alias="created_by_salesman_id")
    _created_at: dt.datetime = field(init=False, factory=get_current_timestamp)
    _assignments: LeadAssignments = field(init=False)
    _notes: Notes = field(init=False)

    @classmethod
    def make(
        cls,
        *,
        id: str,
        customer_id: str,
        created_by_salesman_id: str,
        contact_data: ContactData,
        source: AcquisitionSource,
    ) -> Self:
        notes = Notes()
        assignments = LeadAssignments()
        lead = cls(
            id=id,
            contact_data=contact_data,
            source=source,
            customer_id=customer_id,
            created_by_salesman_id=created_by_salesman_id,
        )
        lead._notes = notes
        lead._assignments = assignments
        return lead

    @classmethod
    def reconstitute(
        cls,
        *,
        id: str,
        customer_id: str,
        created_by_salesman_id: str,
        created_at: dt.datetime,
        contact_data: ContactData,
        source: AcquisitionSource,
        assignments: LeadAssignments,
        notes: Notes,
    ) -> Self:
        lead = cls(
            id=id,
            contact_data=contact_data,
            source=source,
            customer_id=customer_id,
            created_by_salesman_id=created_by_salesman_id,
        )
        lead._created_at = created_at
        lead._notes = notes
        lead._assignments = assignments
        return lead

    @property
    def created_at(self) -> dt.datetime:
        return self._created_at

    @property
    def note(self) -> Note | None:
        return self._notes.most_recent

    @property
    def notes_history(self) -> NotesHistory:
        return self._notes.history

    @property
    def assigned_salesman_id(self) -> str | None:
        return self._assignments.currently_assigned_salesman_id

    @property
    def has_assigned_salesman(self) -> bool:
        return self.assigned_salesman_id is not None

    @property
    def assignment_history(self) -> AssignmentHistory:
        return self._assignments.history

    @property
    def most_recent_assignment(self) -> LeadAssignmentEntry | None:
        return self._assignments.most_recent

    @property
    def created_by_salesman_id(self) -> str:
        return self._created_by_salesman_id

    @property
    def customer_id(self) -> str:
        return self._customer_id

    def assign_salesman(self, new_salesman_id: str, requestor_id: str) -> Self:
        self._check_assignment_permissions(requestor_id)
        self._assignments.change_assigned_salesman(new_salesman_id=new_salesman_id, requestor_id=requestor_id)
        return self

    def change_note(self, new_content: str, editor_id: str) -> Self:
        if not self.has_assigned_salesman or (
            self.has_assigned_salesman and not editor_id == self.assigned_salesman_id
        ):
            raise OnlyOwnerCanEditNotes
        self._notes.change_note(new_content=new_content, editor_id=editor_id)
        return self

    def _check_assignment_permissions(self, requestor_id: str) -> None:
        if self.has_assigned_salesman and self.assigned_salesman_id != requestor_id:
            raise UnauthorizedLeadOwnerChange

    def __str__(self) -> str:
        return f"Lead: {self.contact_data}"
