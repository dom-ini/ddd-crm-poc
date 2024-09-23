import datetime as dt
from typing import Self

from faker import Faker
from pydantic import Field

from building_blocks.application.nested_model import NestedModel
from building_blocks.application.query_model import BaseReadModel
from sales.domain.entities.lead import Lead
from sales.domain.value_objects.acquisition_source import ALLOWED_SOURCE_NAMES
from sales.domain.value_objects.contact_data import ContactData
from sales.domain.value_objects.lead_assignment_entry import LeadAssignmentEntry

faker = Faker(locale="pl_PL")


class ContactDataReadModel(BaseReadModel[ContactData], NestedModel):
    first_name: str = Field(examples=[faker.first_name()])
    last_name: str = Field(examples=[faker.last_name()])
    phone: str | None = Field(default=None, examples=[faker.phone_number()])
    email: str | None = Field(default=None, examples=[faker.email()])

    @classmethod
    def from_domain(cls, entity: ContactData) -> Self:
        return cls(
            first_name=entity.first_name,
            last_name=entity.last_name,
            phone=entity.phone,
            email=entity.email,
        )


class LeadReadModel(BaseReadModel[Lead]):
    id: str = Field(examples=[faker.uuid4()])
    customer_id: str = Field(examples=[faker.uuid4()])
    created_by_salesman_id: str = Field(examples=[faker.uuid4()])
    assigned_salesman_id: str | None = Field(examples=[faker.uuid4()])
    created_at: dt.datetime
    source: str = Field(examples=ALLOWED_SOURCE_NAMES)
    contact_data: ContactDataReadModel = Field(examples=[ContactDataReadModel.get_examples()])

    @classmethod
    def from_domain(cls: Self, entity: Lead) -> Self:
        return cls(
            id=entity.id,
            customer_id=entity.customer_id,
            created_by_salesman_id=entity.created_by_salesman_id,
            created_at=entity.created_at,
            assigned_salesman_id=entity.assigned_salesman_id,
            source=entity.source.name,
            contact_data=ContactDataReadModel.from_domain(entity.contact_data),
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
