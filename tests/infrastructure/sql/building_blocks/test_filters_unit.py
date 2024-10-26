import pytest
from sqlalchemy import select
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from building_blocks.application.exceptions import InvalidFilterType
from building_blocks.application.filters import FilterCondition, FilterConditionType
from building_blocks.infrastructure.exceptions import InvalidFilterField
from building_blocks.infrastructure.sql.filters import SQLFilterService

Base = declarative_base()


class Model(Base):
    __tablename__ = "model"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]


@pytest.fixture()
def model() -> type[Model]:
    return Model


def test_invalid_field_raises_exception(filter_service: SQLFilterService, model: type[Model]) -> None:
    base_query = select(model)
    filter_condition = FilterCondition(field="invalid field", condition_type=FilterConditionType.EQUALS, value="Test")

    with pytest.raises(InvalidFilterField):
        filter_service.get_query_with_filters(model=model, base_query=base_query, filters=[filter_condition])


def test_invalid_condition_type_raises_exception(filter_service: SQLFilterService, model: type[Model]) -> None:
    base_query = select(model)
    filter_condition = FilterCondition(field="name", condition_type="invalid", value="Test")

    with pytest.raises(InvalidFilterType):
        filter_service.get_query_with_filters(model=model, base_query=base_query, filters=[filter_condition])


def test_none_value_filter_ignored(filter_service: SQLFilterService, model: type[Model]):
    base_query = select(model)
    filter_condition = FilterCondition(field="name", condition_type=FilterConditionType.EQUALS, value=None)

    query = filter_service.get_query_with_filters(model=model, base_query=base_query, filters=[filter_condition])

    assert str(query) == str(base_query)
