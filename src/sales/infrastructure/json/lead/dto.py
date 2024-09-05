from attrs import define, field

from building_blocks.infrastructure.dto import BaseDTO
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.domain.entities.lead import Lead
from sales.domain.entities.lead_assignments import LeadAssignments
from sales.domain.entities.notes import Notes
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.contact_data import ContactData
from sales.domain.value_objects.lead_assignment_entry import LeadAssignmentEntry
from sales.infrastructure.json.notes.dto import NoteJsonDTO


@define(kw_only=True)
class AssignmentEntryJsonDTO(BaseDTO[LeadAssignmentEntry, AssignmentReadModel]):
    previous_owner_id: str
    new_owner_id: str
    assigned_by_id: str
    assigned_at: str

    def to_domain(self) -> LeadAssignmentEntry:
        return LeadAssignmentEntry(
            previous_owner_id=self.previous_owner_id,
            new_owner_id=self.new_owner_id,
            assigned_by_id=self.assigned_by_id,
            assigned_at=self.assigned_at,
        )

    def to_read_model(self) -> AssignmentReadModel:
        return AssignmentReadModel(
            previous_owner_id=self.previous_owner_id,
            new_owner_id=self.new_owner_id,
            assigned_by_id=self.assigned_by_id,
            assigned_at=self.assigned_at,
        )


@define(kw_only=True)
class LeadJsonDTO(BaseDTO[Lead, LeadReadModel]):
    id: str
    customer_id: str
    created_by_salesman_id: str
    created_at: str
    source: str
    contact_first_name: str
    contact_last_name: str
    contact_company_name: str
    contact_phone: str | None = None
    contact_email: str | None = None
    assignments: list[AssignmentEntryJsonDTO] = field(
        converter=lambda entries: [AssignmentEntryJsonDTO(**entry) for entry in entries]
    )
    notes: list[NoteJsonDTO] = field(
        converter=lambda notes: [NoteJsonDTO(**note) for note in notes]
    )

    @property
    def assigned_salesman_id(self) -> str | None:
        return self.assignments[-1].new_owner_id if len(self.assignments) else None

    def to_domain(self) -> Lead:
        contact_data = ContactData(
            first_name=self.contact_first_name,
            last_name=self.contact_last_name,
            company_name=self.company_name,
            phone=self.contact_phone,
            email=self.contact_email,
        )
        source = AcquisitionSource(name=self.source)
        assignments = LeadAssignments(history=tuple(self.assignments))
        notes = Notes(history=tuple(self.notes))
        return Lead.reconstitute(
            id=self.id,
            customer_id=self.customer_id,
            created_by_salesman_id=self.created_by_salesman_id,
            created_at=self.created_at,
            contact_data=contact_data,
            source=source,
            assignments=assignments,
            notes=notes,
        )

    def to_read_model(self) -> LeadReadModel:
        return LeadReadModel(
            id=self.id,
            customer_id=self.customer_id,
            created_by_salesman_id=self.created_by_salesman_id,
            assigned_salesman_id=self.assigned_salesman_id,
            created_at=self.created_at,
            source=self.source,
            contact_first_name=self.contact_first_name,
            contact_last_name=self.contact_last_name,
            contact_company_name=self.contact_company_name,
            contact_phone=self.contact_phone,
            contact_email=self.contact_email,
        )
