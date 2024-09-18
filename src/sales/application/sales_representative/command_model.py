from faker import Faker
from pydantic import Field
from building_blocks.application.command_model import BaseCommandModel

faker = Faker(locale="pl_PL")


class SalesRepresentativeCreateModel(BaseCommandModel):
    first_name: str = Field(examples=[faker.first_name()])
    last_name: str = Field(examples=[faker.last_name()])


class SalesRepresentativeUpdateModel(BaseCommandModel):
    first_name: str | None = Field(default=None, examples=[faker.first_name()])
    last_name: str | None = Field(default=None, examples=[faker.last_name()])
