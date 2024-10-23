from collections.abc import Iterable
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from building_blocks.application.exceptions import InvalidData
from building_blocks.infrastructure.exceptions import ObjectAlreadyExists
from sales.domain.entities.notes import NotesHistory
from sales.domain.entities.opportunity import Offer, Opportunity
from sales.domain.repositories.opportunity import OpportunityRepository
from sales.infrastructure.sql.opportunity.models import (
    CurrencyModel,
    OfferItemModel,
    OpportunityModel,
    OpportunityNoteModel,
    ProductModel,
)


def create_comparable_note_entry(note: OpportunityNoteModel) -> Iterable:
    return (note.opportunity_id, note.created_by_id, note.content)


def create_comparable_offer_item_entry(offer_item: OfferItemModel) -> Iterable:
    return (
        offer_item.opportunity_id,
        offer_item.product_id,
        offer_item.currency_id,
        offer_item.amount,
    )


class OpportunitySQLRepository(OpportunityRepository):
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, opportunity_id: str) -> Opportunity | None:
        query = select(OpportunityModel).where(OpportunityModel.id == opportunity_id)
        opportunity = self.db.scalar(query)
        if not opportunity:
            return None
        return opportunity.to_domain()

    def get_all_by_customer(self, customer_id: str) -> Sequence[Opportunity]:
        query = select(OpportunityModel).where(OpportunityModel.customer_id == customer_id)
        opportunities = self.db.scalars(query)
        return opportunities

    def create(self, opportunity: Opportunity) -> None:
        opportunity_in_db = OpportunityModel.from_domain(opportunity)
        offer_items_in_db = self._create_offer_items(opportunity.offer, opportunity_id=opportunity.id)
        try:
            self.db.add_all([opportunity_in_db, *offer_items_in_db])
        except IntegrityError as e:
            raise ObjectAlreadyExists(f"Opportunity with id={opportunity.id} already exists") from e

    def update(self, opportunity: Opportunity) -> None:
        updated_opportunity = OpportunityModel.from_domain(opportunity)
        self.db.merge(updated_opportunity)

        self._update_offer_if_changed(offer=opportunity.offer, opportunity_id=opportunity.id)
        self._update_notes_if_changed(notes_history=opportunity.notes_history, opportunity_id=opportunity.id)

    def _update_offer_if_changed(self, offer: Offer, opportunity_id: str) -> None:
        new_offer = self._create_offer_items(offer, opportunity_id=opportunity_id)
        existing_offer = self._get_offer_items_by_opportunity(opportunity_id)

        new_offer_set = {create_comparable_offer_item_entry(item) for item in new_offer}
        existing_offer_set = {create_comparable_offer_item_entry(item) for item in existing_offer}

        to_delete = existing_offer_set - new_offer_set
        to_add = new_offer_set - existing_offer_set

        for item in existing_offer:
            if create_comparable_offer_item_entry(item) in to_delete:
                self.db.delete(item)
        for item in new_offer:
            if create_comparable_offer_item_entry(item) in to_add:
                self.db.add(item)

    def _update_notes_if_changed(self, notes_history: NotesHistory, opportunity_id: str) -> None:
        new_notes = tuple(
            OpportunityNoteModel.from_domain(note, opportunity_id=opportunity_id) for note in notes_history
        )
        existing_notes = self._get_notes_by_opportunity(opportunity_id)

        new_notes_set = {create_comparable_note_entry(note) for note in new_notes}
        existing_notes_set = {create_comparable_note_entry(note) for note in existing_notes}

        to_add = new_notes_set - existing_notes_set

        for note in new_notes:
            if create_comparable_note_entry(note) in to_add:
                self.db.add(note)

    def _get_notes_by_opportunity(self, opportunity_id: str) -> Iterable[OpportunityNoteModel]:
        query = select(OpportunityNoteModel).where(OpportunityNoteModel.opportunity_id == opportunity_id)
        notes = self.db.scalars(query).all()
        return notes

    def _get_offer_items_by_opportunity(self, opportunity_id: str) -> Iterable[OfferItemModel]:
        query = select(OfferItemModel).where(OfferItemModel.opportunity_id == opportunity_id)
        items = self.db.scalars(query).all()
        return items

    def _create_offer_items(self, offer: Offer, opportunity_id: str) -> Iterable[OfferItemModel]:
        offer_items = []
        for offer_item in offer:
            product_id = self._get_product_id_by_name(offer_item.product.name)
            currency_id = self._get_currency_id_by_iso_code_and_name(
                iso_code=offer_item.value.currency.iso_code,
                name=offer_item.value.currency.name,
            )
            offer_item_in_db = OfferItemModel.from_domain(
                entity=offer_item,
                opportunity_id=opportunity_id,
                product_id=product_id,
                currency_id=currency_id,
            )
            offer_items.append(offer_item_in_db)
        return offer_items

    def _get_product_id_by_name(self, name: str) -> str:
        query = select(ProductModel.id).where(ProductModel.name == name)
        product_id = self.db.scalar(query)
        if not product_id:
            raise InvalidData("Invalid product")
        return product_id

    def _get_currency_id_by_iso_code_and_name(self, iso_code: str, name: str) -> str:
        query = select(CurrencyModel.id).where(CurrencyModel.iso_code == iso_code, CurrencyModel.name == name)
        currency_id = self.db.scalar(query)
        if not currency_id:
            raise InvalidData("Invalid currency")
        return currency_id
