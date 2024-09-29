from collections.abc import Iterator, Sequence
from decimal import Decimal
from uuid import uuid4

import pytest

from building_blocks.application.filters import FilterCondition, FilterConditionType
from sales.application.notes.command_model import NoteCreateModel
from sales.application.opportunity.command import OpportunityCommandUseCase
from sales.application.opportunity.command_model import (
    CurrencyCreateUpdateModel,
    MoneyCreateUpdateModel,
    OfferItemCreateUpdateModel,
    OpportunityCreateModel,
    ProductCreateUpdateModel,
)
from sales.application.opportunity.query_model import OpportunityReadModel
from sales.infrastructure.file.opportunity.command import OpportunityFileUnitOfWork
from sales.infrastructure.file.opportunity.query_service import OpportunityFileQueryService
from tests.infrastructure.file.conftest import TEST_DATA_FOLDER

OPPORTUNITY_QUERY_DB_FILE = "test-query-opportunity"
TEST_DATA_PATH = TEST_DATA_FOLDER / OPPORTUNITY_QUERY_DB_FILE


@pytest.fixture(scope="session")
def command_use_case() -> OpportunityCommandUseCase:
    uow = OpportunityFileUnitOfWork(file_path=TEST_DATA_PATH)
    command_use_case = OpportunityCommandUseCase(opportunity_uow=uow)
    return command_use_case


@pytest.fixture(scope="session")
def offer_item() -> OfferItemCreateUpdateModel:
    product = ProductCreateUpdateModel(name="some product")
    currency = CurrencyCreateUpdateModel(name="US dollar", iso_code="USD")
    value = MoneyCreateUpdateModel(currency=currency, amount=Decimal("100.99"))
    return OfferItemCreateUpdateModel(product=product, value=value)


@pytest.fixture(scope="session", autouse=True)
def opportunity_1(
    command_use_case: OpportunityCommandUseCase,
    salesman_1_id: str,
    offer_item: OfferItemCreateUpdateModel,
    note_content: str,
) -> OpportunityReadModel:
    data = OpportunityCreateModel(customer_id=str(uuid4()), source="ads", priority="medium", offer=[offer_item])
    opportunity = command_use_case.create(data=data, creator_id=salesman_1_id)

    command_use_case.update_note(
        opportunity_id=opportunity.id,
        editor_id=salesman_1_id,
        note_data=NoteCreateModel(content=note_content),
    )

    return opportunity


@pytest.fixture(scope="session", autouse=True)
def opportunity_2(
    command_use_case: OpportunityCommandUseCase,
    salesman_1_id: str,
    offer_item: OfferItemCreateUpdateModel,
) -> OpportunityReadModel:
    data = OpportunityCreateModel(
        customer_id=str(uuid4()),
        source="cold call",
        priority="urgent",
        offer=[offer_item],
    )
    opportunity = command_use_case.create(data=data, creator_id=salesman_1_id)
    return opportunity


@pytest.fixture(scope="session", autouse=True)
def opportunity_3(
    command_use_case: OpportunityCommandUseCase,
    salesman_2_id: str,
    offer_item: OfferItemCreateUpdateModel,
) -> OpportunityReadModel:
    data = OpportunityCreateModel(customer_id=str(uuid4()), source="referral", priority="low", offer=[offer_item])
    opportunity = command_use_case.create(data=data, creator_id=salesman_2_id)
    return opportunity


@pytest.fixture()
def all_opportunities(
    opportunity_1: OpportunityReadModel,
    opportunity_2: OpportunityReadModel,
    opportunity_3: OpportunityReadModel,
) -> Sequence[OpportunityReadModel]:
    return (opportunity_1, opportunity_2, opportunity_3)


@pytest.fixture(scope="session", autouse=True)
def clean_data() -> Iterator[None]:
    yield
    for file in TEST_DATA_FOLDER.iterdir():
        if file.name.startswith(OPPORTUNITY_QUERY_DB_FILE):
            file.unlink()


@pytest.fixture()
def query_service() -> OpportunityFileQueryService:
    return OpportunityFileQueryService(opportunities_file_path=TEST_DATA_PATH)


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
    salesman_1_id: str,
) -> None:
    filters = [
        FilterCondition(
            field="owner_id",
            value=salesman_1_id,
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
