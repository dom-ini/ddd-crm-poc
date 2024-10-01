from collections.abc import Iterable
from operator import attrgetter
from typing import Any, Callable

from building_blocks.application.exceptions import InvalidFilterType
from building_blocks.application.filters import FilterCondition, FilterConditionType


class FileFilterService[Entity]:
    def apply_filters(self, entity: Entity, filters: Iterable[FilterCondition]) -> bool:
        return all(
            self._apply_single_filter(filter.condition_type)(entity, filter.field, filter.value)
            for filter in filters
            if filter.value is not None
        )

    def _apply_single_filter(self, condition_type: str) -> Callable[[Entity, str, Any], bool]:
        if condition_type == FilterConditionType.EQUALS:
            return self._equals
        if condition_type == FilterConditionType.IEQUALS:
            return self._iequals
        if condition_type == FilterConditionType.SEARCH:
            return self._icontains
        raise InvalidFilterType

    def _equals(self, entity: Any, field: str, value: Any) -> bool:
        return value == attrgetter(field)(entity)

    def _iequals(self, entity: Any, field: str, value: Any) -> bool:
        return value.lower() == attrgetter(field)(entity).lower()

    def _icontains(self, entity: Any, field: str, value: Any) -> bool:
        return value.lower().replace(" ", "") in attrgetter(field)(entity).lower().replace(" ", "")
