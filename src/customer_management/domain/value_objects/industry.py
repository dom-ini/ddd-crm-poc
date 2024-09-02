from typing import Literal, get_args
from attrs import define, field
from building_blocks.domain.attrs_validators import attrs_value_in
from building_blocks.domain.value_object import ValueObject


IndustryName = Literal[
    "technology",
    "healthcare",
    "finance",
    "retail",
    "manufacturing",
    "education",
    "real estate",
    "energy",
    "hospitality",
    "transportation & logistics",
    "media & entertainment",
    "non-profit",
    "agriculture",
    "legal services",
    "government",
    "professional services",
    "automotive",
]
ALLOWED_INDUSTRY_NAMES = get_args(IndustryName)


@define(frozen=True, kw_only=True)
class Industry(ValueObject):
    name: IndustryName = field(validator=attrs_value_in(ALLOWED_INDUSTRY_NAMES))

    def __str__(self) -> str:
        return self.name
