from re import L
from faker import Faker
from pydantic import Field
from building_blocks.application.command_model import BaseCommandModel
from sales.domain.value_objects.acquisition_source import (
    ALLOWED_SOURCE_NAMES,
)
from building_blocks.application.nested_model import NestedModel

faker = Faker(locale="pl_PL")


class ContactDataCreateUpdateModel(BaseCommandModel, NestedModel):
    first_name: str = Field(examples=[faker.first_name()])
    last_name: str = Field(examples=[faker.last_name()])
    company_name: str = Field(examples=[faker.company()])
    phone: str | None = Field(default=None, examples=[faker.phone_number()])
    email: str | None = Field(default=None, examples=[faker.email()])


class LeadCreateModel(BaseCommandModel):
    customer_id: str = Field(examples=[faker.uuid4()])
    source: str = Field(examples=ALLOWED_SOURCE_NAMES)
    contact_data: ContactDataCreateUpdateModel = Field(
        examples=[ContactDataCreateUpdateModel.get_examples()]
    )


class LeadUpdateModel(BaseCommandModel):
    source: str | None = Field(default=None, examples=ALLOWED_SOURCE_NAMES)
    contact_data: ContactDataCreateUpdateModel | None = Field(
        default=None, examples=[ContactDataCreateUpdateModel.get_examples()]
    )


class AssignmentUpdateModel(BaseCommandModel):
    new_salesman_id: str
