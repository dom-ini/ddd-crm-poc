from collections.abc import Iterable
from attrs import define, field
from building_blocks.domain.entity import EntityWithoutId
from building_blocks.domain.utils.date import get_current_timestamp
from sales.domain.value_objects.note import Note


NotesHistory = Iterable[Note]


@define(eq=False, kw_only=True)
class Notes(EntityWithoutId):
    _history: NotesHistory = field(alias="history", factory=tuple)

    @property
    def most_recent(self) -> Note | None:
        if len(self.history) == 0:
            return None
        return self._history[-1]

    @property
    def history(self) -> NotesHistory:
        return self._history

    def change_note(self, new_content: str, editor_id: str) -> None:
        note = self._create_note(content=new_content, editor_id=editor_id)
        self._history = self._history + (note,)

    def _create_note(self, content: str, editor_id: str) -> Note:
        return Note(
            content=content, created_by_id=editor_id, created_at=get_current_timestamp()
        )

    def __str__(self) -> str:
        return f'Notes, most recent: "{self.most_recent}"'
