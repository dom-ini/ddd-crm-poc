import datetime as dt
from typing import Self

from faker import Faker
from pydantic import Field


from building_blocks.application.query_model import BaseReadModel
from sales.domain.entities.lead import Lead
from sales.domain.value_objects.acquisition_source import ALLOWED_SOURCE_NAMES
from sales.domain.value_objects.lead_assignment_entry import LeadAssignmentEntry

faker = Faker(locale="pl_PL")


class LeadReadModel(BaseReadModel[Lead]):
    id: str = Field(examples=[faker.uuid4()])
    customer_id: str = Field(examples=[faker.uuid4()])
    created_by_salesman_id: str = Field(examples=[faker.uuid4()])
    assigned_salesman_id: str | None = Field(examples=[faker.uuid4()])
    created_at: dt.datetime
    source: str = Field(examples=ALLOWED_SOURCE_NAMES)
    contact_first_name: str = Field(examples=[faker.first_name()])
    contact_last_name: str = Field(examples=[faker.last_name()])
    contact_company_name: str = Field(examples=[faker.company()])
    contact_phone: str | None = Field(default=None, examples=[faker.phone_number()])
    contact_email: str | None = Field(default=None, examples=[faker.email()])

    @classmethod
    def from_domain(cls: Self, entity: Lead) -> Self:
        return cls(
            id=entity.id,
            customer_id=entity.customer_id,
            created_by_salesman_id=entity.created_by_salesman_id,
            created_at=entity.created_at,
            assigned_salesman_id=entity.assigned_salesman_id,
            source=entity.source.name,
            contact_first_name=entity.contact_data.first_name,
            contact_last_name=entity.contact_data.last_name,
            contact_company_name=entity.contact_data.company_name,
            contact_phone=entity.contact_data.phone,
            contact_email=entity.contact_data.email,
        )


class AssignmentReadModel(BaseReadModel[LeadAssignmentEntry]):
    previous_owner_id: str | None = Field(default=None, examples=[faker.uuid4()])
    new_owner_id: str = Field(examples=[faker.uuid4()])
    assigned_by_id: str = Field(examples=[faker.uuid4()])
    assigned_at: dt.datetime

    @classmethod
    def from_domain(cls: Self, entity: LeadAssignmentEntry) -> Self:
        return cls(
            previous_owner_id=entity.previous_owner_id,
            new_owner_id=entity.new_owner_id,
            assigned_by_id=entity.assigned_by_id,
            assigned_at=entity.assigned_at,
        )
