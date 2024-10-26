from collections.abc import Iterable
from operator import attrgetter
from typing import Any, Callable, TypeVar

from building_blocks.application.filters import BaseFilterResolver, FilterCondition, FilterConditionType
from building_blocks.infrastructure.exceptions import InvalidFilterField

EntityT = TypeVar("EntityT")
FilterFunc = Callable[[type[EntityT], str, Any], bool]


def _get_field_value(obj: EntityT, field_name: str) -> Any:
    try:
        return attrgetter(field_name)(obj)
    except AttributeError as e:
        raise InvalidFilterField(field_name) from e


def equals(entity: EntityT, field: str, value: Any) -> bool:
    return value == _get_field_value(entity, field)


def iequals(entity: EntityT, field: str, value: Any) -> bool:
    return value.lower() == _get_field_value(entity, field).lower()


def search(entity: EntityT, field: str, value: Any) -> bool:
    return value.lower().replace(" ", "") in _get_field_value(entity, field).lower().replace(" ", "")


class FileFilterResolver(BaseFilterResolver[FilterFunc]):
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
