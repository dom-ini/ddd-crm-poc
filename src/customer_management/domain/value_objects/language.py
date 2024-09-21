from attrs import define

from building_blocks.domain.value_object import ValueObject


@define(frozen=True, kw_only=True)
class Language(ValueObject):
    code: str
    name: str

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
