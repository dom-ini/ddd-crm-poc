from unittest.mock import MagicMock

import pytest

from building_blocks.application.exceptions import ObjectDoesNotExist
from sales.application.sales_representative.query import SalesRepresentativeQueryUseCase
from sales.application.sales_representative.query_service import SalesRepresentativeQueryService


@pytest.fixture()
def mock_sr_query_service() -> SalesRepresentativeQueryService:
    return MagicMock(SalesRepresentativeQueryService)


@pytest.fixture()
def sr_query_use_case(
    mock_sr_query_service: SalesRepresentativeQueryService,
) -> SalesRepresentativeQueryUseCase:
    return SalesRepresentativeQueryUseCase(sr_query_service=mock_sr_query_service)


@pytest.mark.parametrize("method_name", ["get"])
def test_calling_method_wrong_sales_representative_id_should_fail(
    sr_query_use_case: SalesRepresentativeQueryUseCase,
    mock_sr_query_service: SalesRepresentativeQueryService,
    method_name: str,
) -> None:
    sales_representative_id = "invalid id"
    getattr(mock_sr_query_service, method_name).return_value = None

    with pytest.raises(ObjectDoesNotExist):
        getattr(sr_query_use_case, method_name)(sales_representative_id)
