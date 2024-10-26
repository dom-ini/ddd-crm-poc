import datetime as dt
from typing import Self

from faker import Faker
from pydantic import Field

from building_blocks.application.query_model import BaseReadModel
from sales.domain.value_objects.note import Note

faker = Faker(locale="pl_PL")


class NoteReadModel(BaseReadModel[Note]):
    created_by_id: str = Field(examples=[faker.uuid4()])
    content: str = Field(examples=[faker.text(max_nb_chars=30)])
    created_at: dt.datetime

    @classmethod
    def from_domain(cls, entity: Note) -> Self:
        return cls(
            created_by_id=entity.created_by_id,
            content=entity.content,
            created_at=entity.created_at,
        )
