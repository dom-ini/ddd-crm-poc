from faker import Faker
from pydantic import Field

from building_blocks.application.command_model import BaseCommandModel

faker = Faker(locale="pl_PL")


class NoteCreateModel(BaseCommandModel):
    content: str = Field(examples=[faker.text(max_nb_chars=30)])
