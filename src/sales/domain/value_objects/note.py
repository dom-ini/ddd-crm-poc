import datetime as dt

from attrs import define

from building_blocks.domain.value_object import ValueObject


@define(frozen=True, kw_only=True)
class Note(ValueObject):
    _printable_content_length = 20

    created_by_id: str
    content: str
    created_at: dt.datetime

    def __str__(self) -> str:
        suffix = "..." if len(self.content) > self._printable_content_length else ""
        return f"{self.content[: self._printable_content_length] + suffix}"
