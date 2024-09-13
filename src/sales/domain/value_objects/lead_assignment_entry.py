import datetime as dt
from attrs import define, field
from building_blocks.domain.utils.date import get_current_timestamp
from building_blocks.domain.value_object import ValueObject


@define(frozen=True, kw_only=True)
class LeadAssignmentEntry(ValueObject):
    previous_owner_id: str | None
    new_owner_id: str
    assigned_by_id: str
    assigned_at: dt.datetime

    def __str__(self) -> str:
        return f"Assignment from: {self.previous_owner_id} to: {self.new_owner_id}"
