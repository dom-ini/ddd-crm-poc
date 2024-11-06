from collections.abc import Iterable
from operator import attrgetter
from typing import Any, Callable, TypeVar

from sqlalchemy import ColumnElement, Select, func

from building_blocks.application.filters import BaseFilterResolver, FilterCondition, FilterConditionType
from building_blocks.infrastructure.exceptions import InvalidFilterField
from building_blocks.infrastructure.sql.db import Base

MainModelT = TypeVar("MainModelT", bound=Base)
FilterField = Any
InternalFilterFunc = Callable[[FilterField, Any], ColumnElement[bool]]
FilterFunc = Callable[[Any], ColumnElement[bool]]
RelatedModels = set[type[MainModelT]]
ResolvedFilter = tuple[FilterFunc, RelatedModels]
FilterResolverFunc = Callable[[type[MainModelT], str], ResolvedFilter]
ResolvedFilterExpression = tuple[ColumnElement[bool], RelatedModels]


def resolve_model_field_and_relationships(
    field_name: str,
    model: type[MainModelT],
) -> tuple[FilterField, RelatedModels]:
    field_names = field_name.split(".")
    related_models: RelatedModels = set()
    current_model = model
    remaining_field_name = field_name

    for i, current_field in enumerate(field_names):
        try:
            final_field = attrgetter(remaining_field_name)(current_model)
            break
        except AttributeError as e:
            if not hasattr(current_model, current_field):
                raise InvalidFilterField(field=field_name) from e

            relationship = attrgetter(current_field)(current_model)
            if not hasattr(relationship, "mapper"):
                raise InvalidFilterField(field=field_name) from e

            current_model = relationship.mapper.class_
            related_models.add(current_model)
            remaining_field_name = ".".join(field_names[i + 1 :])

    return final_field, related_models


def equals(field: FilterField, value: Any) -> ColumnElement[bool]:
    return field == value


def iequals(field: FilterField, value: Any) -> ColumnElement[bool]:
    return func.lower(value) == func.lower(field)


def search(field: FilterField, value: Any) -> ColumnElement[bool]:
    return func.replace(func.lower(field), " ", "").contains(func.replace(func.lower(value), " ", ""))


def build_filter_expression(
    filter_func: InternalFilterFunc,
    model: type[MainModelT],
    field_name: str,
) -> ResolvedFilter:
    model_field, related_models = resolve_model_field_and_relationships(field_name=field_name, model=model)
    return lambda value: filter_func(model_field, value), related_models


class SQLFilterResolver(BaseFilterResolver[FilterResolverFunc]):
    _filter_mapping = {
        FilterConditionType.EQUALS: lambda model, field_name: build_filter_expression(
            filter_func=equals, model=model, field_name=field_name
        ),
        FilterConditionType.IEQUALS: lambda model, field_name: build_filter_expression(
            filter_func=iequals, model=model, field_name=field_name
        ),
        FilterConditionType.SEARCH: lambda model, field_name: build_filter_expression(
            filter_func=search, model=model, field_name=field_name
        ),
    }


class SQLFilterService:
    resolver = SQLFilterResolver()

    def get_query_with_filters(
        self,
        model: type[MainModelT],
        base_query: Select,
        filters: Iterable[FilterCondition],
    ) -> Select:
        models_to_join: RelatedModels = set()
        for filter_ in filters:
            if filter_.value is None:
                continue

            filter_expression, related_models = self._resolve_filter(model, filter_)
            base_query = base_query.where(filter_expression)
            models_to_join |= related_models

        return self._apply_joins(base_query, models_to_join)

    def _resolve_filter(self, model: type[MainModelT], filter_: FilterCondition) -> ResolvedFilterExpression:
        resolve_filter = self.resolver.resolve(filter_.condition_type)
        filter_expression, related_models = resolve_filter(model, filter_.field)
        return filter_expression(filter_.value), related_models

    def _apply_joins(self, query: Select, models_to_join: RelatedModels) -> Select:
        for model_to_join in models_to_join:
            query = query.join(model_to_join)
        return query
