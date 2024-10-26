from typing import Sequence

import pytest

from building_blocks.infrastructure.file.vo_service import FileValueObjectService
from sales.application.opportunity.query_model import ProductReadModel
from tests.infrastructure.file.conftest import VO_TEST_DATA_PATH

pytestmark = pytest.mark.integration


@pytest.fixture()
def vo_service() -> FileValueObjectService:
    return FileValueObjectService(file_path=VO_TEST_DATA_PATH, read_model=ProductReadModel)


@pytest.fixture()
def all_products(product_1: ProductReadModel, product_2: ProductReadModel) -> Sequence[ProductReadModel]:
    return (product_1, product_2)


def test_get_all(vo_service: FileValueObjectService, all_products: Sequence[ProductReadModel]) -> None:
    products = vo_service.get_all()

    assert len(products) == len(all_products)
    assert all(product in products for product in all_products)
