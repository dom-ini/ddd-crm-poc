from collections.abc import Iterable
from typing import Callable

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from building_blocks.infrastructure.exceptions import ObjectAlreadyExists
from sales.domain.entities.lead import Lead
from sales.domain.entities.lead_assignments import AssignmentHistory
from sales.domain.entities.notes import NotesHistory
from sales.domain.repositories.lead import LeadRepository
from sales.infrastructure.sql.lead.models import LeadAssignmentEntryModel, LeadModel, LeadNoteModel


def create_comparable_note_entry(note: LeadNoteModel) -> Iterable:
    return (note.lead_id, note.created_by_id, note.content)


def create_comparable_lead_assignment_entry(
    assignment: LeadAssignmentEntryModel,
) -> Iterable:
    return (assignment.lead_id, assignment.new_owner_id, assignment.assigned_by_id)


class LeadSQLRepository(LeadRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, lead_id: str) -> Lead | None:
        query = select(LeadModel).where(LeadModel.id == lead_id)
        lead = self.db.scalar(query)
        if not lead:
            return None
        return lead.to_domain()

    def get_for_customer(self, customer_id: str) -> Lead | None:
        query = select(LeadModel).where(LeadModel.customer_id == customer_id)
        lead = self.db.scalar(query)
        if not lead:
            return None
        return lead.to_domain()

    def create(self, lead: Lead) -> None:
        lead_in_db = LeadModel.from_domain(lead)
        try:
            self.db.add(lead_in_db)
        except IntegrityError as e:
            raise ObjectAlreadyExists(f"Lead with id={lead.id} already exists") from e

    def update(self, lead: Lead) -> None:
        updated_lead = LeadModel.from_domain(lead)
        self.db.merge(updated_lead)

        self._update_lead_assignments_if_changed(assignment_history=lead.assignment_history, lead_id=lead.id)
        self._update_notes_if_changed(notes_history=lead.notes_history, lead_id=lead.id)

    def _update_if_changed[
        EntityModelT
    ](
        self,
        new_entities: Iterable[EntityModelT],
        existing_entities: Iterable[EntityModelT],
        comparator_factory: Callable[[EntityModelT], Iterable],
    ) -> None:
        new_entities_set = {comparator_factory(entity) for entity in new_entities}
        existing_entities_set = {comparator_factory(entity) for entity in existing_entities}

        to_add = new_entities_set - existing_entities_set

        for entity in new_entities:
            if comparator_factory(entity) in to_add:
                self.db.add(entity)

    def _update_lead_assignments_if_changed(self, assignment_history: AssignmentHistory, lead_id: str) -> None:
        new_assignments = tuple(
            LeadAssignmentEntryModel.from_domain(assignment, lead_id=lead_id) for assignment in assignment_history
        )
        existing_assignments = self._get_assignments_by_lead(lead_id)
        self._update_if_changed(
            new_entities=new_assignments,
            existing_entities=existing_assignments,
            comparator_factory=create_comparable_lead_assignment_entry,
        )

    def _update_notes_if_changed(self, notes_history: NotesHistory, lead_id: str) -> None:
        new_notes = tuple(LeadNoteModel.from_domain(note, lead_id=lead_id) for note in notes_history)
        existing_notes = self._get_notes_by_lead(lead_id)
        self._update_if_changed(
            new_entities=new_notes,
            existing_entities=existing_notes,
            comparator_factory=create_comparable_note_entry,
        )

    def _get_assignments_by_lead(self, lead_id: str) -> Iterable[LeadAssignmentEntryModel]:
        query = select(LeadAssignmentEntryModel).where(LeadAssignmentEntryModel.lead_id == lead_id)
        assignments = self.db.scalars(query).all()
        return assignments

    def _get_notes_by_lead(self, lead_id: str) -> Iterable[LeadNoteModel]:
        query = select(LeadNoteModel).where(LeadNoteModel.lead_id == lead_id)
        notes = self.db.scalars(query).all()
        return notes
