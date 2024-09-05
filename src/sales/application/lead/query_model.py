import datetime as dt
from typing import Self


from building_blocks.application.query_model import BaseReadModel
from sales.domain.entities.lead import Lead
from sales.domain.value_objects.lead_assignment_entry import LeadAssignmentEntry


class LeadReadModel(BaseReadModel[Lead]):
    id: str
    customer_id: str
    created_by_salesman_id: str
    assigned_salesman_id: str | None
    created_at: dt.datetime
    source: str
    contact_first_name: str
    contact_last_name: str
    contact_company_name: str
    contact_phone: str | None = None
    contact_email: str | None = None

    @classmethod
    def from_domain(cls: Self, entity: Lead) -> Self:
        return cls(
            id=str(entity.id),
            customer_id=str(entity.customer_id),
            created_by_salesman_id=str(entity.created_by_salesman_id),
            created_at=entity.created_at,
            assigned_salesman_id=str(entity.assigned_salesman_id),
            source=entity.source.name,
            contact_first_name=entity.contact_data.first_name,
            contact_last_name=entity.contact_data.last_name,
            contact_company_name=entity.contact_data.company_name,
            contact_phone=entity.contact_data.phone,
            contact_email=entity.contact_data.email,
        )


class AssignmentReadModel(BaseReadModel[LeadAssignmentEntry]):
    previous_owner_id: str | None = None
    new_owner_id: str
    assigned_by_id: str
    assigned_at: dt.datetime

    @classmethod
    def from_domain(cls: Self, entity: LeadAssignmentEntry) -> Self:
        return cls(
            previous_owner_id=entity.previous_owner_id,
            new_owner_id=entity.new_owner_id,
            assigned_by_id=entity.assigned_by_id,
            assigned_at=entity.assigned_at,
        )
