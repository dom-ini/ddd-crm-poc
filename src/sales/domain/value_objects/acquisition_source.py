from typing import Literal, get_args
from attrs import define, field
from building_blocks.domain.attrs_validators import attrs_value_in
from building_blocks.domain.value_object import ValueObject


SourceName = Literal[
    "social media", "website", "cold call", "ads", "referral", "event", "other"
]
ALLOWED_SOURCE_NAMES = get_args(SourceName)


@define(frozen=True, kw_only=True)
class AcquisitionSource(ValueObject):
    name: SourceName = field(validator=attrs_value_in(ALLOWED_SOURCE_NAMES))

    def __str__(self) -> str:
        return self.name
