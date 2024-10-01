from enum import Enum
from typing import Any

from attrs import define


class FilterConditionType(str, Enum):
    EQUALS = "equals"
    IEQUALS = "iequals"
    SEARCH = "search"


@define
class FilterCondition:
    field: str
    value: Any
    condition_type: FilterConditionType
