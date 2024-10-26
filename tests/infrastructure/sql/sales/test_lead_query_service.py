from collections.abc import Callable, Sequence
from typing import ContextManager

import pytest
from sqlalchemy.orm import Session

from building_blocks.application.filters import FilterCondition, FilterConditionType
from sales.application.lead.query_model import LeadReadModel
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from sales.infrastructure.sql.lead.query_service import LeadSQLQueryService

pytestmark = pytest.mark.integration


@pytest.fixture()
def all_leads(lead_1: LeadReadModel, lead_2: LeadReadModel) -> Sequence[LeadReadModel]:
    return (lead_1, lead_2)


@pytest.fixture()
def query_service(session_factory: Callable[[], ContextManager[Session]]) -> LeadSQLQueryService:
    return LeadSQLQueryService(session_factory)


def test_get_lead(query_service: LeadSQLQueryService, lead_1: LeadReadModel) -> None:
    lead = query_service.get(lead_id=lead_1.id)

    assert lead is not None
    assert lead.id == lead_1.id


def test_get_all(query_service: LeadSQLQueryService, all_leads: Sequence[LeadReadModel]) -> None:
    leads = query_service.get_all()

    fetched_leads_ids = set(lead.id for lead in leads)
    leads_ids = set(lead.id for lead in all_leads)
    assert fetched_leads_ids == leads_ids


def test_get_filtered(query_service: LeadSQLQueryService, lead_1: LeadReadModel, lead_2: LeadReadModel) -> None:
    filters = [
        FilterCondition(
            field="contact_data.first_name",
            value="Jan",
            condition_type=FilterConditionType.EQUALS,
        )
    ]
    leads = query_service.get_filtered(filters)

    fetched_leads_ids = set(lead.id for lead in leads)
    assert fetched_leads_ids == {lead_1.id}


def test_get_assignment_history(
    query_service: LeadSQLQueryService,
    lead_1: LeadReadModel,
    representative_3: SalesRepresentativeReadModel,
) -> None:
    assignments = query_service.get_assignment_history(lead_id=lead_1.id)

    assert assignments is not None
    assert assignments[0].new_owner_id == representative_3.id


def test_get_notes(query_service: LeadSQLQueryService, lead_1: LeadReadModel, note_content: str) -> None:
    notes = query_service.get_notes(lead_id=lead_1.id)

    assert notes is not None
    assert notes[0].content == note_content


@pytest.mark.parametrize("method_name", ["get", "get_assignment_history", "get_notes"])
def test_methods_should_return_none_if_not_found(query_service: LeadSQLQueryService, method_name: str) -> None:
    lead = getattr(query_service, method_name)(lead_id="invalid id")

    assert lead is None
