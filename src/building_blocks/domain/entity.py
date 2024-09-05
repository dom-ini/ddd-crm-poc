from typing import Any

from uuid import UUID, uuid4

from attrs import define


@define(eq=False, kw_only=True)
class Entity:
    id: UUID

    def __eq__(self, value: Any) -> bool:
        if isinstance(value, type(self)):
            return self.id == value.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)


@define(eq=False, kw_only=True)
class EntityWithoutId:
    pass


@define(eq=False, kw_only=True, frozen=True)
class ReadOnlyEntity(Entity):
    pass


@define(eq=False, kw_only=True)
class AggregateRoot(Entity):
    pass
