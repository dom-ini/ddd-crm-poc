from collections.abc import Iterable
from operator import attrgetter
from typing import Any, Callable, TypeVar

from building_blocks.application.filters import BaseFilterResolver, FilterCondition, FilterConditionType

EntityT = TypeVar("EntityT")
FilterFunc = Callable[[type[EntityT], str, Any], bool]


def equals(entity: EntityT, field: str, value: Any) -> bool:
    return value == attrgetter(field)(entity)


def iequals(entity: EntityT, field: str, value: Any) -> bool:
    return value.lower() == attrgetter(field)(entity).lower()


def search(entity: EntityT, field: str, value: Any) -> bool:
    return value.lower().replace(" ", "") in attrgetter(field)(entity).lower().replace(" ", "")


class FileFilterResolver(BaseFilterResolver):
    _filter_mapping = {
        FilterConditionType.EQUALS: equals,
        FilterConditionType.IEQUALS: iequals,
        FilterConditionType.SEARCH: search,
    }


class FileFilterService:
    resolver = FileFilterResolver()

    def apply_filters(self, entity: EntityT, filters: Iterable[FilterCondition]) -> bool:
        return all(
            self.resolver.resolve(filter.condition_type)(entity, filter.field, filter.value)
            for filter in filters
            if filter.value is not None
        )
