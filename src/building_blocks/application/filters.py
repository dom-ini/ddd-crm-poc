from abc import ABC
from enum import Enum
from typing import Any

from attrs import define

from building_blocks.application.exceptions import InvalidFilterType


class FilterConditionType(str, Enum):
    EQUALS = "equals"
    IEQUALS = "iequals"
    SEARCH = "search"


@define
class FilterCondition:
    field: str
    value: Any
    condition_type: FilterConditionType


class BaseFilterResolver[FilterFuncT](ABC):
    _filter_mapping: dict[FilterConditionType, FilterFuncT]

    def resolve(self, condition_type: FilterConditionType) -> FilterFuncT:
        if condition_type not in self._filter_mapping:
            raise InvalidFilterType
        return self._filter_mapping[condition_type]
