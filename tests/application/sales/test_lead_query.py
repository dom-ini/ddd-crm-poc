from unittest.mock import MagicMock

import pytest

from building_blocks.application.exceptions import ObjectDoesNotExist
from sales.application.lead.query import LeadQueryUseCase
from sales.application.lead.query_service import LeadQueryService


@pytest.fixture()
def mock_lead_query_service() -> LeadQueryService:
    return MagicMock(LeadQueryService)


@pytest.fixture()
def lead_query_use_case(mock_lead_query_service: LeadQueryService) -> LeadQueryUseCase:
    return LeadQueryUseCase(lead_query_service=mock_lead_query_service)


@pytest.mark.parametrize("method_name", ["get", "get_notes", "get_assignment_history"])
def test_calling_method_with_wrong_lead_id_should_fail(
    lead_query_use_case: LeadQueryUseCase,
    mock_lead_query_service: LeadQueryService,
    method_name: str,
) -> None:
    lead_id = "invalid id"
    getattr(mock_lead_query_service, method_name).return_value = None

    with pytest.raises(ObjectDoesNotExist):
        getattr(lead_query_use_case, method_name)(lead_id)
