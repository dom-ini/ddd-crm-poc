from uuid import UUID
from attrs import define, field
from building_blocks.domain.entity import Entity
from sales.domain.value_objects.note import Note


NotesHistory = tuple[Note]


@define(eq=False, kw_only=True)
class Notes(Entity):
    _history: NotesHistory = field(alias="history", factory=tuple)

    @property
    def most_recent(self) -> Note | None:
        if len(self.history) == 0:
            return None
        return self._history[-1]

    @property
    def history(self) -> NotesHistory:
        return self._history

    def change_note(self, new_content: str, editor_id: UUID) -> None:
        note = self._create_note(content=new_content, editor_id=editor_id)
        self._history = self._history + (note,)

    def _create_note(self, content: str, editor_id: UUID) -> Note:
        return Note(content=content, created_by_id=editor_id)

    def __str__(self) -> str:
        return f'Notes, most recent: "{self.most_recent}"'
