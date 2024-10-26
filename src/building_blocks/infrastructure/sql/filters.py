from collections.abc import Iterable
from operator import attrgetter
from typing import Any, Callable, TypeVar

from sqlalchemy import ColumnElement, Select, func

from building_blocks.application.filters import BaseFilterResolver, FilterCondition, FilterConditionType
from building_blocks.infrastructure.exceptions import InvalidFilterField

MainModelT = TypeVar("MainModelT")
FilterFunc = Callable[[type[MainModelT], str, Any], ColumnElement[bool]]


def _resolve_field(field_name: str, model: type[MainModelT]) -> Any:
    field_names = field_name.split(".")

    base_model = model
    nested_field_name = ".".join(field_names)

    for i, current_field in enumerate(field_names):
        try:
            final_field = attrgetter(nested_field_name)(base_model)
            break
        except AttributeError as e:
            if not hasattr(base_model, current_field):
                raise InvalidFilterField(field=field_name) from e
            relationship = attrgetter(current_field)(base_model)
            if not hasattr(relationship, "mapper"):
                raise InvalidFilterField(field=field_name) from e
            base_model = relationship.mapper.class_
            nested_field_name = ".".join(field_names[i + 1 :])

    return final_field


def equals(model: type[MainModelT], field: str, value: Any) -> ColumnElement[bool]:
    model_field = _resolve_field(field_name=field, model=model)
    return model_field == value


def iequals(model: type[MainModelT], field: str, value: Any) -> ColumnElement[bool]:
    model_field = _resolve_field(field_name=field, model=model)
    return func.lower(value) == func.lower(model_field)


def search(model: type[MainModelT], field: str, value: Any) -> ColumnElement[bool]:
    model_field = _resolve_field(field_name=field, model=model)
    return func.replace(func.lower(model_field), " ", "").contains(func.replace(func.lower(value), " ", ""))


class SQLFilterResolver(BaseFilterResolver[FilterFunc]):
    _filter_mapping = {
        FilterConditionType.EQUALS: equals,
        FilterConditionType.IEQUALS: iequals,
        FilterConditionType.SEARCH: search,
    }


class SQLFilterService:
    resolver = SQLFilterResolver()

    def get_query_with_filters(
        self,
        model: type[MainModelT],
        base_query: Select,
        filters: Iterable[FilterCondition],
    ) -> Select:
        for filter_ in filters:
            if filter_.value is None:
                continue
            filter_func = self.resolver.resolve(filter_.condition_type)
            base_query = base_query.where(filter_func(model, filter_.field, filter_.value))
        return base_query
