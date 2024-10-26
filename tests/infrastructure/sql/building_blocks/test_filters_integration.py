from collections.abc import Callable
from typing import ContextManager

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from building_blocks.application.filters import FilterCondition, FilterConditionType
from building_blocks.infrastructure.sql.filters import SQLFilterService
from sales.domain.value_objects.product import Product
from sales.infrastructure.sql.opportunity.models import ProductModel

pytestmark = pytest.mark.integration


@pytest.fixture()
def product_model() -> type[ProductModel]:
    return ProductModel


@pytest.mark.parametrize(
    "filter_type,name_transformer",
    [
        (FilterConditionType.EQUALS, lambda x: x),
        (FilterConditionType.IEQUALS, lambda x: x.upper()),
        (FilterConditionType.SEARCH, lambda x: x.upper().replace(" ", "")[-3:]),
    ],
)
@pytest.mark.usefixtures("product_2")
def test_filter_applied_correctly(
    filter_service: SQLFilterService,
    product_model: type[ProductModel],
    product_1: Product,
    session_factory: Callable[[], ContextManager[Session]],
    filter_type: FilterConditionType,
    name_transformer: Callable[[str], str],
):
    base_query = select(product_model)
    filter_condition = FilterCondition(
        field="name",
        condition_type=filter_type,
        value=name_transformer(product_1.name),
    )

    query = filter_service.get_query_with_filters(
        model=product_model, base_query=base_query, filters=[filter_condition]
    )
    with session_factory() as db:
        products = tuple(db.scalars(query))

    assert len(products) == 1
    assert products[0].name == product_1.name
