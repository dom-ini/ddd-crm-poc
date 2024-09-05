from typing import Self
import datetime as dt

from building_blocks.application.query_model import BaseReadModel
from sales.domain.value_objects.note import Note


class NoteReadModel(BaseReadModel[Note]):
    created_by_id: str
    content: str
    created_at: dt.datetime

    @classmethod
    def from_domain(cls: Self, entity: Note) -> Self:
        return cls(
            created_by_id=entity.created_by_id,
            content=entity.content,
            created_at=entity.created_at,
        )
