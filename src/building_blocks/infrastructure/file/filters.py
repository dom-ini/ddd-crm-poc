from collections.abc import Iterable
from operator import attrgetter
from typing import Any, Callable

from building_blocks.application.filters import (
    FilterCondition,
    FilterConditionType,
)
from building_blocks.application.exceptions import InvalidFilterType


class FileFilterService[Entity]:
    def apply_filters(self, entity: Entity, filters: Iterable[FilterCondition]) -> bool:
        return all(
            self._apply_single_filter(filter.condition_type)(
                entity, filter.field, filter.value
            )
            for filter in filters
            if filter.value is not None
        )

    def _apply_single_filter(self, type: str) -> Callable[[Entity, str, Any], bool]:
        if type == FilterConditionType.EQUALS:
            return self._equals
        if type == FilterConditionType.SEARCH:
            return self._icontains
        raise InvalidFilterType

    def _equals(self, entity: Any, field: str, value: Any) -> bool:
        return attrgetter(field)(entity) == value

    def _icontains(self, entity: Any, field: str, value: Any) -> bool:
        return value.lower().replace(" ", "") in attrgetter(field)(
            entity
        ).lower().replace(" ", "")
