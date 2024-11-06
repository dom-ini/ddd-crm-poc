import datetime as dt
from types import SimpleNamespace
from typing import Any, Optional, Self

from sqlalchemy import ForeignKey, SQLColumnExpression, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from building_blocks.infrastructure.sql.db import Base
from sales.domain.entities.lead import Lead
from sales.domain.entities.lead_assignments import LeadAssignments
from sales.domain.entities.notes import Notes
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.contact_data import ContactData
from sales.domain.value_objects.lead_assignment_entry import LeadAssignmentEntry
from sales.domain.value_objects.note import Note
from sales.infrastructure.sql.notes.models import BaseNoteModel


class LeadNoteModel(BaseNoteModel):
    __tablename__ = "lead_note"

    lead_id: Mapped[str] = mapped_column(ForeignKey("lead.id"), nullable=False, index=True, primary_key=True)

    lead: Mapped["LeadModel"] = relationship(back_populates="notes")

    @classmethod
    def from_domain(cls, entity: Note, **kwargs: str) -> Self:
        return cls(
            lead_id=kwargs["lead_id"],
            created_by_id=entity.created_by_id,
            created_at=entity.created_at,
            content=entity.content,
        )


class LeadAssignmentEntryModel(Base[LeadAssignmentEntry]):
    __tablename__ = "lead_assignment"

    lead_id: Mapped[str] = mapped_column(ForeignKey("lead.id"), nullable=False, index=True, primary_key=True)
    previous_owner_id: Mapped[Optional[str]]
    new_owner_id: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    assigned_by_id: Mapped[str] = mapped_column(nullable=False, primary_key=True)

    assigned_at: Mapped[dt.datetime] = mapped_column(nullable=False)

    lead: Mapped["LeadModel"] = relationship(back_populates="assignments")

    def to_domain(self) -> LeadAssignmentEntry:
        return LeadAssignmentEntry(
            previous_owner_id=self.previous_owner_id,
            new_owner_id=self.new_owner_id,
            assigned_by_id=self.assigned_by_id,
            assigned_at=self.assigned_at,
        )

    @classmethod
    def from_domain(cls, entity: LeadAssignmentEntry, **kwargs: str) -> Self:
        return cls(
            lead_id=kwargs["lead_id"],
            previous_owner_id=entity.previous_owner_id,
            new_owner_id=entity.new_owner_id,
            assigned_by_id=entity.assigned_by_id,
            assigned_at=entity.assigned_at,
        )


class LeadModel(Base[Lead]):
    __tablename__ = "lead"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[str] = mapped_column(nullable=False, index=True)
    created_by_id: Mapped[str] = mapped_column(nullable=False, index=True)

    created_at: Mapped[dt.datetime] = mapped_column(nullable=False)
    source_name: Mapped[str] = mapped_column(nullable=False)
    contact_data_first_name: Mapped[str] = mapped_column(nullable=False)
    contact_data_last_name: Mapped[str] = mapped_column(nullable=False)
    contact_data_phone: Mapped[Optional[str]]
    contact_data_email: Mapped[Optional[str]]

    notes: Mapped[list["LeadNoteModel"]] = relationship(back_populates="lead")
    assignments: Mapped[list["LeadAssignmentEntryModel"]] = relationship(back_populates="lead")

    @hybrid_property
    def assigned_salesman_id(self) -> str | None:
        if not self.assignments:
            return None
        return self.assignments[-1].new_owner_id

    @assigned_salesman_id.inplace.expression
    @classmethod
    def _assigned_salesman_id_expression(cls) -> SQLColumnExpression[str | None]:
        return (
            select(LeadAssignmentEntryModel.new_owner_id)
            .where(LeadAssignmentEntryModel.lead_id == cls.id)
            .order_by(LeadAssignmentEntryModel.assigned_at.desc())
            .limit(1)
            .correlate(cls)
            .scalar_subquery()
        )

    @hybrid_property
    def contact_data(self) -> SimpleNamespace:
        return SimpleNamespace(
            first_name=self.contact_data_first_name,
            last_name=self.contact_data_last_name,
            phone=self.contact_data_phone,
            email=self.contact_data_email,
        )

    def to_domain(self) -> Lead:
        contact_data = ContactData(
            first_name=self.contact_data_first_name,
            last_name=self.contact_data_last_name,
            phone=self.contact_data_phone,
            email=self.contact_data_email,
        )
        source = AcquisitionSource(name=self.source_name)
        assignments = LeadAssignments(history=tuple(assignment.to_domain() for assignment in self.assignments))
        notes = Notes(history=tuple(note.to_domain() for note in self.notes))

        return Lead.reconstitute(
            id=self.id,
            customer_id=self.customer_id,
            created_by_salesman_id=self.created_by_id,
            created_at=self.created_at,
            contact_data=contact_data,
            source=source,
            assignments=assignments,
            notes=notes,
        )

    @classmethod
    def from_domain(cls, entity: Lead, **kwargs: Any) -> Self:
        return cls(
            id=entity.id,
            customer_id=entity.customer_id,
            created_by_id=entity.created_by_salesman_id,
            created_at=entity.created_at,
            source_name=entity.source.name,
            contact_data_first_name=entity.contact_data.first_name,
            contact_data_last_name=entity.contact_data.last_name,
            contact_data_phone=entity.contact_data.phone,
            contact_data_email=entity.contact_data.email,
        )
