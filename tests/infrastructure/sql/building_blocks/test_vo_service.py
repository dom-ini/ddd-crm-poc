from collections.abc import Callable, Sequence
from typing import ContextManager

import pytest
from sqlalchemy.orm import Session

from building_blocks.infrastructure.sql.vo_service import SQLValueObjectService
from sales.application.opportunity.query_model import ProductReadModel
from sales.domain.value_objects.product import Product
from sales.infrastructure.sql.opportunity.models import ProductModel

pytestmark = pytest.mark.integration


@pytest.fixture()
def vo_service(session_factory: Callable[[], ContextManager[Session]]) -> SQLValueObjectService:
    return SQLValueObjectService(session_factory=session_factory, model=ProductModel, read_model=ProductReadModel)


@pytest.fixture()
def all_products(product_1: Product, product_2: Product) -> Sequence[Product]:
    return (product_1, product_2)


def test_get_all(vo_service: SQLValueObjectService, all_products: Sequence[Product]) -> None:
    products = vo_service.get_all()

    assert len(products) == len(all_products)
    assert set(product.name for product in products) == set(product.name for product in all_products)
