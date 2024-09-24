from typing import Self

from attrs import define

from building_blocks.domain.entity import AggregateRoot
from sales.domain.exceptions import SalesRepresentativeCanOnlyModifyItsOwnData


@define(eq=False, kw_only=True)
class SalesRepresentative(AggregateRoot):
    first_name: str
    last_name: str

    @classmethod
    def reconstitute(cls, id: str, first_name: str, last_name: str) -> Self:
        return cls(id=id, first_name=first_name, last_name=last_name)

    def update(self, editor_id: str, first_name: str | None = None, last_name: str | None = None) -> None:
        self._check_update_permissions(editor_id)
        if first_name is not None:
            self.first_name = first_name
        if last_name is not None:
            self.last_name = last_name

    def _check_update_permissions(self, editor_id: str) -> None:
        if editor_id != self.id:
            raise SalesRepresentativeCanOnlyModifyItsOwnData
