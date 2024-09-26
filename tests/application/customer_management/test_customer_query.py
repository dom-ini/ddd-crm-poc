from unittest.mock import MagicMock

import pytest

from building_blocks.application.exceptions import ObjectDoesNotExist
from customer_management.application.query import CustomerQueryUseCase
from customer_management.application.query_service import CustomerQueryService


@pytest.fixture()
def mock_customer_query_service() -> CustomerQueryService:
    return MagicMock(CustomerQueryService)


@pytest.fixture()
def customer_query_use_case(
    mock_customer_query_service: CustomerQueryService,
) -> CustomerQueryUseCase:
    return CustomerQueryUseCase(customer_query_service=mock_customer_query_service)


@pytest.mark.parametrize("method_name", ["get", "get_contact_persons"])
def test_calling_method_with_wrong_customer_id_should_fail(
    customer_query_use_case: CustomerQueryUseCase,
    mock_customer_query_service: CustomerQueryService,
    method_name: str,
) -> None:
    customer_id = "invalid id"
    getattr(mock_customer_query_service, method_name).return_value = None

    with pytest.raises(ObjectDoesNotExist):
        getattr(customer_query_use_case, method_name)(customer_id)
