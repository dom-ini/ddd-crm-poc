import datetime as dt

from attrs import define, field
from building_blocks.domain.utils.date import get_current_timestamp
from building_blocks.domain.value_object import ValueObject


@define(frozen=True, kw_only=True)
class Note(ValueObject):
    _PRINTABLE_CONTENT_LENGTH: int = field(default=20, init=False)

    created_by_id: str
    content: str
    created_at: dt.datetime

    def __str__(self) -> str:
        suffix = "..." if len(self.content) > self._PRINTABLE_CONTENT_LENGTH else ""
        return f"{self.content[: self._PRINTABLE_CONTENT_LENGTH] + suffix}"
