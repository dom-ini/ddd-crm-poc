from typing import Self

from attrs import define

from building_blocks.domain.entity import AggregateRoot


@define(eq=False, kw_only=True)
class SalesRepresentative(AggregateRoot):
    first_name: str
    last_name: str

    @classmethod
    def reconstitute(cls, id: str, first_name: str, last_name: str) -> Self:
        return cls(id=id, first_name=first_name, last_name=last_name)
