from attrs import define

from building_blocks.infrastructure.dto import BaseDTO
from sales.application.notes.query_model import NoteReadModel
from sales.domain.value_objects.note import Note


@define(kw_only=True)
class NoteJsonDTO(BaseDTO[Note, NoteReadModel]):
    created_by_id: str
    content: str
    created_at: str

    def to_domain(self) -> Note:
        return Note(
            created_by_id=self.created_by_id,
            content=self.content,
            created_at=self.created_at,
        )

    def to_read_model(self) -> NoteReadModel:
        return NoteReadModel(
            created_by_id=self.created_by_id,
            content=self.content,
            created_at=self.created_at,
        )
