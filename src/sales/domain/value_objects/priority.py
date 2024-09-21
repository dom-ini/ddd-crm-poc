from typing import Literal, get_args

from attrs import define, field

from building_blocks.domain.attrs_validators import attrs_value_in
from building_blocks.domain.value_object import ValueObject

PriorityLevel = Literal["low", "medium", "high", "urgent"]
ALLOWED_PRIORITY_LEVELS = get_args(PriorityLevel)


@define(frozen=True, kw_only=True)
class Priority(ValueObject):
    level: PriorityLevel = field(validator=attrs_value_in(ALLOWED_PRIORITY_LEVELS))

    def __str__(self) -> str:
        return self.level
