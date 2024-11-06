from collections.abc import Sequence

import pytest

from building_blocks.application.filters import FilterCondition, FilterConditionType
from sales.application.opportunity.command_model import OfferItemCreateUpdateModel
from sales.application.opportunity.query_model import OpportunityReadModel
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel
from sales.infrastructure.file.opportunity.query_service import OpportunityFileQueryService
from tests.fixtures.file.db_fixtures import FILE_OPPORTUNITY_TEST_DATA_PATH


@pytest.fixture()
def all_opportunities(
    opportunity_1: OpportunityReadModel,
    opportunity_2: OpportunityReadModel,
    opportunity_3: OpportunityReadModel,
) -> Sequence[OpportunityReadModel]:
    return (opportunity_1, opportunity_2, opportunity_3)


@pytest.fixture()
def query_service() -> OpportunityFileQueryService:
    return OpportunityFileQueryService(opportunities_file_path=FILE_OPPORTUNITY_TEST_DATA_PATH)


def test_get_opportunity(query_service: OpportunityFileQueryService, opportunity_1: OpportunityReadModel) -> None:
    opportunity = query_service.get(opportunity_id=opportunity_1.id)

    assert opportunity is not None
    assert opportunity.id == opportunity_1.id


def test_get_all(
    query_service: OpportunityFileQueryService,
    all_opportunities: Sequence[OpportunityReadModel],
) -> None:
    opportunities = query_service.get_all()

    fetched_opportunitys_ids = set(opportunity.id for opportunity in opportunities)
    opportunitys_ids = set(opportunity.id for opportunity in all_opportunities)
    assert fetched_opportunitys_ids == opportunitys_ids


def test_get_filtered(
    query_service: OpportunityFileQueryService,
    opportunity_1: OpportunityReadModel,
    opportunity_2: OpportunityReadModel,
    representative_1: SalesRepresentativeReadModel,
) -> None:
    filters = [
        FilterCondition(
            field="owner_id",
            value=representative_1.id,
            condition_type=FilterConditionType.EQUALS,
        )
    ]
    opportunities = query_service.get_filtered(filters)

    fetched_opportunities_ids = set(opportunity.id for opportunity in opportunities)
    assert fetched_opportunities_ids == {opportunity_1.id, opportunity_2.id}


def test_get_notes(
    query_service: OpportunityFileQueryService,
    opportunity_1: OpportunityReadModel,
    note_content: str,
) -> None:
    notes = query_service.get_notes(opportunity_id=opportunity_1.id)

    assert notes is not None
    assert notes[0].content == note_content


def test_get_offer(
    query_service: OpportunityFileQueryService,
    opportunity_1: OpportunityReadModel,
    offer_item: OfferItemCreateUpdateModel,
) -> None:
    offer = query_service.get_offer(opportunity_id=opportunity_1.id)

    assert offer is not None
    assert offer[0].product.name == offer_item.product.name
    assert offer[0].value.amount == offer_item.value.amount


@pytest.mark.parametrize("method_name", ["get", "get_offer", "get_notes"])
def test_methods_should_return_none_if_not_found(query_service: OpportunityFileQueryService, method_name: str) -> None:
    opportunity = getattr(query_service, method_name)(opportunity_id="invalid id")

    assert opportunity is None
