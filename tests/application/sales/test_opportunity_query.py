from unittest.mock import MagicMock

import pytest

from building_blocks.application.exceptions import ObjectDoesNotExist
from sales.application.opportunity.query import OpportunityQueryUseCase
from sales.application.opportunity.query_service import OpportunityQueryService


@pytest.fixture()
def mock_opportunity_query_service() -> OpportunityQueryService:
    return MagicMock(OpportunityQueryService)


@pytest.fixture()
def opportunity_query_use_case(
    mock_opportunity_query_service: OpportunityQueryService,
) -> OpportunityQueryUseCase:
    return OpportunityQueryUseCase(opportunity_query_service=mock_opportunity_query_service)


@pytest.mark.parametrize("method_name", ["get", "get_notes", "get_offer"])
def test_calling_method_wrong_opportunity_id_should_fail(
    opportunity_query_use_case: OpportunityQueryUseCase,
    mock_opportunity_query_service: OpportunityQueryService,
    method_name: str,
) -> None:
    opportunity_id = "invalid id"
    getattr(mock_opportunity_query_service, method_name).return_value = None

    with pytest.raises(ObjectDoesNotExist):
        getattr(opportunity_query_use_case, method_name)(opportunity_id)
