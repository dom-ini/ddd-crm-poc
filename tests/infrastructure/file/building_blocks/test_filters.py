import pytest
from attrs import define

from building_blocks.application.filters import FilterCondition, FilterConditionType
from building_blocks.infrastructure.file.filters import FileFilterService


@define
class Model:
    field_1: str
    field_2: str


class FilterService(FileFilterService):
    pass


@pytest.fixture()
def filter_service() -> FilterService:
    return FilterService()


@pytest.fixture()
def model() -> Model:
    return Model(field_1="some string", field_2="SoMe OtHeR StRinG")


def test_filter_equals_with_match_should_return_true(filter_service: FilterService, model: Model) -> None:
    filters = [
        FilterCondition(
            field="field_1",
            value="some string",
            condition_type=FilterConditionType.EQUALS,
        )
    ]

    assert filter_service.apply_filters(entity=model, filters=filters)


def test_filter_equals_with_no_match_should_return_false(filter_service: FilterService, model: Model) -> None:
    filters = [
        FilterCondition(
            field="field_1",
            value="no match",
            condition_type=FilterConditionType.EQUALS,
        )
    ]

    assert not filter_service.apply_filters(entity=model, filters=filters)


def test_filter_iequals_with_match_should_return_true(filter_service: FilterService, model: Model) -> None:
    filters = [
        FilterCondition(
            field="field_1",
            value="SOME STRING",
            condition_type=FilterConditionType.IEQUALS,
        )
    ]

    assert filter_service.apply_filters(entity=model, filters=filters)


def test_filter_iequals_with_no_match_should_return_false(filter_service: FilterService, model: Model) -> None:
    filters = [
        FilterCondition(
            field="field_1",
            value="no match",
            condition_type=FilterConditionType.IEQUALS,
        )
    ]

    assert not filter_service.apply_filters(entity=model, filters=filters)


def test_filter_search_with_match_should_return_true(filter_service: FilterService, model: Model) -> None:
    filters = [
        FilterCondition(
            field="field_2",
            value="otherstring",
            condition_type=FilterConditionType.SEARCH,
        )
    ]

    assert filter_service.apply_filters(entity=model, filters=filters)


def test_filter_search_with_no_match_should_return_false(filter_service: FilterService, model: Model) -> None:
    filters = [
        FilterCondition(
            field="field_1",
            value="no match",
            condition_type=FilterConditionType.SEARCH,
        )
    ]

    assert not filter_service.apply_filters(entity=model, filters=filters)


def test_multiple_filters_with_all_matching_should_return_true(filter_service: FilterService, model: Model) -> None:
    filters = [
        FilterCondition(
            field="field_1",
            value="some string",
            condition_type=FilterConditionType.EQUALS,
        ),
        FilterCondition(
            field="field_1",
            value="SOME STRING",
            condition_type=FilterConditionType.IEQUALS,
        ),
        FilterCondition(
            field="field_2",
            value="string",
            condition_type=FilterConditionType.SEARCH,
        ),
    ]

    assert filter_service.apply_filters(entity=model, filters=filters)


def test_multiple_filters_with_some_matching_should_return_false(filter_service: FilterService, model: Model) -> None:
    filters = [
        FilterCondition(
            field="field_1",
            value="some string",
            condition_type=FilterConditionType.EQUALS,
        ),
        FilterCondition(
            field="field_2",
            value="no match",
            condition_type=FilterConditionType.SEARCH,
        ),
    ]

    assert not filter_service.apply_filters(entity=model, filters=filters)


def test_multiple_filters_with_none_matching_should_return_false(filter_service: FilterService, model: Model) -> None:
    filters = [
        FilterCondition(
            field="field_1",
            value="no match",
            condition_type=FilterConditionType.EQUALS,
        ),
        FilterCondition(
            field="field_2",
            value="no match",
            condition_type=FilterConditionType.SEARCH,
        ),
    ]

    assert not filter_service.apply_filters(entity=model, filters=filters)
