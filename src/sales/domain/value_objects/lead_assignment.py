import datetime as dt
from uuid import UUID
from attrs import define, field
from building_blocks.domain.utils.date import get_current_timestamp
from building_blocks.domain.value_object import ValueObject


@define(frozen=True, kw_only=True)
class LeadAssignment(ValueObject):
    previous_owner_id: UUID | None
    current_owner_id: UUID
    assigned_by_id: UUID
    assigned_at: dt.datetime = field(init=False, factory=get_current_timestamp)

    def __str__(self) -> str:
        return f"Assignment from: {self.previous_owner_id} to: {self.current_owner_id}"
