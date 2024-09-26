import datetime as dt
from decimal import Decimal

import pytest

from building_blocks.domain.exceptions import ValueNotAllowed
from sales.domain.entities.notes import Notes
from sales.domain.entities.opportunity import Offer, Opportunity
from sales.domain.exceptions import (
    AmountMustBeGreaterThanZero,
    OnlyOwnerCanEditNotes,
    OnlyOwnerCanModifyOffer,
    OnlyOwnerCanModifyOpportunityData,
)
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.money.currency import Currency
from sales.domain.value_objects.money.money import Money
from sales.domain.value_objects.note import Note
from sales.domain.value_objects.offer_item import OfferItem
from sales.domain.value_objects.opportunity_stage import OpportunityStage
from sales.domain.value_objects.priority import Priority
from sales.domain.value_objects.product import Product


@pytest.fixture()
def stage() -> OpportunityStage:
    return OpportunityStage(name="proposal")


@pytest.fixture()
def priority() -> Priority:
    return Priority(level="high")


@pytest.fixture()
def stage_2() -> OpportunityStage:
    return OpportunityStage(name="closed-lost")


@pytest.fixture()
def priority_2() -> Priority:
    return Priority(level="urgent")


@pytest.fixture()
def product() -> Product:
    return Product(name="Product 1")


@pytest.fixture()
def currency() -> Currency:
    return Currency(name="US dollar", iso_code="USD")


@pytest.fixture()
def offer_item_value(currency: Currency) -> Money:
    return Money(currency=currency, amount=Decimal("99.99"))


@pytest.fixture()
def offer_item(product: Product, offer_item_value: Money) -> OfferItem:
    return OfferItem(product=product, value=offer_item_value)


@pytest.fixture()
def offer(offer_item: OfferItem) -> Offer:
    return (offer_item,)


@pytest.fixture()
def opportunity(
    source: AcquisitionSource,
    stage: OpportunityStage,
    priority: Priority,
    offer: Offer,
) -> Opportunity:
    return Opportunity.make(
        id="opportunity_1",
        created_by_id="salesman_1",
        customer_id="customer_1",
        source=source,
        stage=stage,
        priority=priority,
        offer=offer,
    )


def test_stage_creation_with_invalid_name_should_fail() -> None:
    with pytest.raises(ValueNotAllowed):
        OpportunityStage(name="invalid stage")


def test_priority_creation_with_invalid_level_should_fail() -> None:
    with pytest.raises(ValueNotAllowed):
        Priority(level="invalid priority")


@pytest.mark.parametrize("amount", [0, -100])
def test_money_creation_with_invalid_amount_should_fail(currency: Currency, amount: int) -> None:
    with pytest.raises(AmountMustBeGreaterThanZero):
        Money(currency=currency, amount=Decimal(amount))


def test_opportunity_creation(
    opportunity: Opportunity,
    source: AcquisitionSource,
    stage: OpportunityStage,
    priority: Priority,
    offer: Offer,
) -> None:
    assert opportunity.id == "opportunity_1"
    assert opportunity.source == source
    assert opportunity.stage == stage
    assert opportunity.priority == priority
    assert opportunity.offer == offer
    assert opportunity.created_by_id == "salesman_1"
    assert isinstance(opportunity._created_at, dt.datetime)
    assert opportunity.note is None


def test_opportunity_reconstitution(
    source: AcquisitionSource,
    stage: OpportunityStage,
    priority: Priority,
    offer: Offer,
    note: Note,
) -> None:
    notes = Notes(history=(note,))
    created_at = dt.datetime(2023, 1, 1)

    opportunity = Opportunity.reconstitute(
        id="opportunity_1",
        created_by_id="salesman_1",
        customer_id="customer_1",
        owner_id="salesman_1",
        created_at=created_at,
        source=source,
        stage=stage,
        priority=priority,
        offer=offer,
        notes=notes,
    )

    assert opportunity.id == "opportunity_1"
    assert opportunity.source == source
    assert opportunity.stage == stage
    assert opportunity.priority == priority
    assert opportunity.offer == offer
    assert opportunity.created_by_id == "salesman_1"
    assert opportunity.owner_id == "salesman_1"
    assert opportunity.created_at == created_at
    assert opportunity.note == note


def test_opportunity_update(
    opportunity: Opportunity,
    source_2: AcquisitionSource,
    stage_2: OpportunityStage,
    priority_2: Priority,
) -> None:
    opportunity.update(
        editor_id=opportunity.owner_id,
        source=source_2,
        stage=stage_2,
        priority=priority_2,
    )

    assert opportunity.source == source_2
    assert opportunity.stage == stage_2
    assert opportunity.priority == priority_2


def test_opportunity_partial_update(
    opportunity: Opportunity,
    stage_2: OpportunityStage,
) -> None:
    old_source = opportunity.source
    old_priority = opportunity.priority

    opportunity.update(editor_id=opportunity.owner_id, stage=stage_2)

    assert opportunity.stage == stage_2
    assert opportunity.source == old_source
    assert opportunity.priority == old_priority


def test_opportunity_update_by_non_owner_should_fail(opportunity: Opportunity, stage_2: OpportunityStage) -> None:
    with pytest.raises(OnlyOwnerCanModifyOpportunityData):
        opportunity.update(editor_id="non owner id", stage=stage_2)


def test_change_note_by_owner(opportunity: Opportunity) -> None:
    opportunity.change_note(new_content="Updated Note", editor_id=opportunity.owner_id)
    assert opportunity.note.content == "Updated Note"


def test_change_note_by_non_owner_should_fail(opportunity: Opportunity) -> None:
    with pytest.raises(OnlyOwnerCanEditNotes):
        opportunity.change_note(new_content="Unauthorized Note Change", editor_id="salesman_2")


def test_modify_offer(opportunity: Opportunity, offer_item: OfferItem) -> None:
    old_offer = opportunity.offer
    new_offer = (offer_item, offer_item)
    opportunity.modify_offer(new_offer=new_offer, editor_id=opportunity.owner_id)

    assert all(item == new_item for item, new_item in zip(opportunity.offer, new_offer))
    assert opportunity.offer != old_offer


def test_modify_offer_by_non_owner_should_fail(opportunity: Opportunity, offer_item: OfferItem) -> None:
    new_offer = (offer_item, offer_item)
    with pytest.raises(OnlyOwnerCanModifyOffer):
        opportunity.modify_offer(new_offer=new_offer, editor_id="salesman_2")
