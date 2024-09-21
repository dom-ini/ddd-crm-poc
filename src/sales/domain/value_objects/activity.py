import datetime as dt
from typing import Literal, get_args

from attrs import define, field

from building_blocks.domain.attrs_validators import attrs_value_in
from building_blocks.domain.utils.date import DEFAULT_DATE_FORMAT

ActivityType = Literal["email", "call", "meeting", "proposal"]
ALLOWED_ACTIVITY_TYPES = get_args(ActivityType)


@define(frozen=True, kw_only=True)
class Activity:
    _date_format: str = field(init=False, default=DEFAULT_DATE_FORMAT)

    opportunity_id = str
    undertaken_by_id: str
    activity_type: ActivityType = field(validator=attrs_value_in(ALLOWED_ACTIVITY_TYPES))
    undertaken_at: dt.datetime
    description: str | None = None

    def __str__(self) -> str:
        return f"Activity: {self.activity_type}, at {self.undertaken_at.strftime(self._date_format)}"
