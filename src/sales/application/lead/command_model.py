from faker import Faker
from pydantic import Field
from building_blocks.application.command_model import BaseCommandModel
from sales.domain.value_objects.acquisition_source import (
    ALLOWED_SOURCE_NAMES,
)

faker = Faker(locale="pl_PL")


class LeadCreateModel(BaseCommandModel):
    customer_id: str = Field(examples=[faker.uuid4()])
    source: str = Field(examples=ALLOWED_SOURCE_NAMES)
    contact_first_name: str = Field(examples=[faker.first_name()])
    contact_last_name: str = Field(examples=[faker.last_name()])
    contact_company_name: str = Field(examples=[faker.company()])
    contact_phone: str | None = Field(default=None, examples=[faker.phone_number()])
    contact_email: str | None = Field(default=None, examples=[faker.email()])


class LeadUpdateModel(BaseCommandModel):
    source: str = Field(examples=ALLOWED_SOURCE_NAMES)
    contact_first_name: str = Field(examples=[faker.first_name()])
    contact_last_name: str = Field(examples=[faker.last_name()])
    contact_company_name: str = Field(examples=[faker.company()])
    contact_phone: str | None = Field(default=None, examples=[faker.phone_number()])
    contact_email: str | None = Field(default=None, examples=[faker.email()])


class AssignmentUpdateModel(BaseCommandModel):
    new_salesman_id: str
