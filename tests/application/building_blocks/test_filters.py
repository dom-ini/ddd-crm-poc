from collections.abc import Callable

import pytest

from building_blocks.application.exceptions import InvalidFilterType
from building_blocks.application.filters import BaseFilterResolver, FilterConditionType

FilterFunction = Callable[[], str]

DEFINED_CONDITION_TYPE = FilterConditionType.EQUALS


def get_fixed_value() -> FilterFunction:
    return "some fixed value"


class CustomFilterResolver(BaseFilterResolver[FilterFunction]):
    _filter_mapping = {DEFINED_CONDITION_TYPE: get_fixed_value}


@pytest.fixture()
def resolver() -> CustomFilterResolver:
    return CustomFilterResolver()


@pytest.fixture()
def filter_function() -> FilterFunction:
    return get_fixed_value


@pytest.fixture()
def condition_type() -> FilterConditionType:
    return DEFINED_CONDITION_TYPE


def test_resolve_returns_correct_filter_function(
    resolver: CustomFilterResolver, filter_function: FilterFunction, condition_type: FilterConditionType
) -> None:
    resolved_function = resolver.resolve(condition_type)

    assert resolved_function() == filter_function()


def test_resolve_with_wrong_condition_type_should_fail(resolver: CustomFilterResolver) -> None:
    with pytest.raises(InvalidFilterType):
        resolver.resolve(FilterConditionType.SEARCH)
