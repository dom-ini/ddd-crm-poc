from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from building_blocks.application.exceptions import InvalidData
from building_blocks.infrastructure.exceptions import ObjectAlreadyExists
from sales.domain.entities.opportunity import Opportunity
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.money.currency import Currency
from sales.domain.value_objects.money.money import Money
from sales.domain.value_objects.offer_item import OfferItem
from sales.domain.value_objects.opportunity_stage import OpportunityStage
from sales.domain.value_objects.priority import Priority
from sales.domain.value_objects.product import Product
from sales.infrastructure.sql.opportunity.repository import OpportunitySQLRepository

pytestmark = pytest.mark.integration


@pytest.fixture()
def opportunity_repo(session: Session) -> OpportunitySQLRepository:
    return OpportunitySQLRepository(session)


@pytest.fixture()
def invalid_product() -> Product:
    return Product(name="invalid")


@pytest.fixture()
def invalid_currency() -> Currency:
    return Currency(iso_code="invalid", name="invalid")


@pytest.fixture()
def offer_item(product_1: Product, currency: Currency) -> OfferItem:
    offer_item = OfferItem(product=product_1, value=Money(currency=currency, amount=Decimal("100.00")))
    return offer_item


@pytest.fixture()
def offer_item_with_invalid_product(invalid_product: Product, currency: Currency) -> OfferItem:
    offer_item = OfferItem(product=invalid_product, value=Money(currency=currency, amount=Decimal("100.00")))
    return offer_item


@pytest.fixture()
def offer_item_with_invalid_currency(product_1: Product, invalid_currency: Currency) -> OfferItem:
    offer_item = OfferItem(product=product_1, value=Money(currency=invalid_currency, amount=Decimal("100.00")))
    return offer_item


@pytest.fixture()
def opportunity(offer_item: OfferItem) -> Opportunity:
    opportunity = Opportunity.make(
        id="some id",
        created_by_id="salesman 1",
        customer_id="customer 1",
        source=AcquisitionSource(name="ads"),
        stage=OpportunityStage(name="negotiation"),
        priority=Priority(level="low"),
        offer=(offer_item,),
    )
    return opportunity


@pytest.fixture()
def opportunity_2(offer_item: OfferItem) -> Opportunity:
    opportunity = Opportunity.make(
        id="some id 2",
        created_by_id="salesman 1",
        customer_id="customer 2",
        source=AcquisitionSource(name="ads"),
        stage=OpportunityStage(name="negotiation"),
        priority=Priority(level="low"),
        offer=(offer_item,),
    )
    return opportunity


@pytest.fixture()
def opportunity_with_invalid_product(offer_item_with_invalid_product: OfferItem) -> Opportunity:
    opportunity = Opportunity.make(
        id="some id",
        created_by_id="salesman 1",
        customer_id="customer 1",
        source=AcquisitionSource(name="ads"),
        stage=OpportunityStage(name="negotiation"),
        priority=Priority(level="low"),
        offer=(offer_item_with_invalid_product,),
    )
    return opportunity


@pytest.fixture()
def opportunity_with_invalid_currency(offer_item_with_invalid_currency: OfferItem) -> Opportunity:
    opportunity = Opportunity.make(
        id="some id",
        created_by_id="salesman 1",
        customer_id="customer 1",
        source=AcquisitionSource(name="ads"),
        stage=OpportunityStage(name="negotiation"),
        priority=Priority(level="low"),
        offer=(offer_item_with_invalid_currency,),
    )
    return opportunity


def test_create_and_get(opportunity_repo: OpportunitySQLRepository, opportunity: Opportunity) -> None:
    opportunity_repo.create(opportunity)

    fetched_opportunity = opportunity_repo.get(opportunity.id)

    assert fetched_opportunity is not None
    assert fetched_opportunity.id == opportunity.id


def test_create_with_invalid_product_should_fail(
    opportunity_repo: OpportunitySQLRepository, opportunity_with_invalid_product: Opportunity
) -> None:
    with pytest.raises(InvalidData):
        opportunity_repo.create(opportunity_with_invalid_product)


def test_create_with_invalid_currency_should_fail(
    opportunity_repo: OpportunitySQLRepository, opportunity_with_invalid_currency: Opportunity
) -> None:
    with pytest.raises(InvalidData):
        opportunity_repo.create(opportunity_with_invalid_currency)


def test_get_all_by_customer(
    opportunity_repo: OpportunitySQLRepository, opportunity: Opportunity, opportunity_2: Opportunity
) -> None:
    opportunity_repo.create(opportunity)
    opportunity_repo.create(opportunity_2)

    opportunities = list(opportunity_repo.get_all_by_customer(customer_id=opportunity.customer_id))

    assert len(opportunities) == 1
    assert opportunities[0].id == opportunity.id
    assert opportunity_2.id not in tuple(opportunity.id for opportunity in opportunities)


def test_get_should_return_none_if_not_found(
    opportunity_repo: OpportunitySQLRepository,
) -> None:
    fetched_opportunity = opportunity_repo.get("invalid id")

    assert fetched_opportunity is None


def test_create_with_existing_id_should_fail(
    opportunity_repo: OpportunitySQLRepository, opportunity: Opportunity
) -> None:
    opportunity_repo.create(opportunity)

    with pytest.raises(ObjectAlreadyExists):
        opportunity_repo.create(opportunity)


def test_update(opportunity_repo: OpportunitySQLRepository, opportunity: Opportunity) -> None:
    new_source = AcquisitionSource(name="other")
    opportunity_repo.create(opportunity)
    opportunity.update(editor_id=opportunity.owner_id, source=new_source)

    opportunity_repo.update(opportunity)

    fetched_opportunity = opportunity_repo.get(opportunity.id)
    assert fetched_opportunity.source == new_source


def test_update_updates_notes(opportunity_repo: OpportunitySQLRepository, opportunity: Opportunity) -> None:
    new_note_content = "this is a note"
    opportunity_repo.create(opportunity)
    opportunity.change_note(new_content=new_note_content, editor_id=opportunity.owner_id)

    opportunity_repo.update(opportunity)
    opportunity_repo.db.flush()

    fetched_opportunity = opportunity_repo.get(opportunity.id)
    assert fetched_opportunity.note.content == new_note_content


def test_update_updates_offer(
    opportunity_repo: OpportunitySQLRepository, opportunity: Opportunity, product_2: Product, currency: Currency
) -> None:
    new_offer_item = OfferItem(product=product_2, value=Money(currency=currency, amount=Decimal("999.99")))
    opportunity_repo.create(opportunity)
    opportunity.modify_offer(editor_id=opportunity.owner_id, new_offer=(new_offer_item,))

    opportunity_repo.update(opportunity)
    opportunity_repo.db.flush()

    fetched_opportunity = opportunity_repo.get(opportunity.id)
    offer_item = fetched_opportunity.offer[0]
    assert offer_item.product == product_2
    assert offer_item.value.amount == Decimal("999.99")


def test_update_with_invalid_product_should_fail(
    opportunity_repo: OpportunitySQLRepository, opportunity: Opportunity, invalid_product: Product, currency: Currency
) -> None:
    new_offer_item = OfferItem(product=invalid_product, value=Money(currency=currency, amount=Decimal("999.99")))
    opportunity_repo.create(opportunity)
    opportunity.modify_offer(editor_id=opportunity.owner_id, new_offer=(new_offer_item,))

    with pytest.raises(InvalidData):
        opportunity_repo.update(opportunity)


def test_update_with_invalid_currency_should_fail(
    opportunity_repo: OpportunitySQLRepository,
    opportunity: Opportunity,
    product_1: Product,
    invalid_currency: Currency,
) -> None:
    new_offer_item = OfferItem(product=product_1, value=Money(currency=invalid_currency, amount=Decimal("999.99")))
    opportunity_repo.create(opportunity)
    opportunity.modify_offer(editor_id=opportunity.owner_id, new_offer=(new_offer_item,))

    with pytest.raises(InvalidData):
        opportunity_repo.update(opportunity)
