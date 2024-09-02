from attrs import define
from building_blocks.domain.value_object import ValueObject


@define(frozen=True, kw_only=True)
class Currency(ValueObject):
    name: str
    iso_code: str

    def __str__(self) -> str:
        return f"{self.iso_code} - {self.name}"
