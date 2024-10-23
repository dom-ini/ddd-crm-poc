import datetime as dt
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, Self

from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from building_blocks.infrastructure.sql.db import Base
from building_blocks.infrastructure.sql.utils import generate_uuid
from sales.domain.entities.notes import Notes
from sales.domain.entities.opportunity import Opportunity
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.money.currency import Currency
from sales.domain.value_objects.money.money import Money
from sales.domain.value_objects.note import Note
from sales.domain.value_objects.offer_item import OfferItem
from sales.domain.value_objects.opportunity_stage import OpportunityStage
from sales.domain.value_objects.priority import Priority
from sales.domain.value_objects.product import Product
from sales.infrastructure.sql.notes.models import BaseNoteModel


class ProductModel(Base[Product]):
    __tablename__ = "product"

    id: Mapped[str] = mapped_column(default=generate_uuid, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    def to_domain(self) -> Product:
        return Product(name=self.name)

    @classmethod
    def from_domain(cls, entity: Product, **kwargs: Any) -> Self:
        return cls(name=entity.name)


class CurrencyModel(Base[Currency]):
    __tablename__ = "currency"

    id: Mapped[str] = mapped_column(default=generate_uuid, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(nullable=False)
    iso_code: Mapped[str] = mapped_column(String(3), nullable=False, unique=True)

    def to_domain(self) -> Currency:
        return Currency(name=self.name, iso_code=self.iso_code)

    @classmethod
    def from_domain(cls, entity: Currency, **kwargs: Any) -> Self:
        return cls(name=entity.name, iso_code=entity.iso_code)


class OfferItemModel(Base[OfferItem]):
    __tablename__ = "offer_item"

    opportunity_id: Mapped[str] = mapped_column(
        ForeignKey("opportunity.id"), nullable=False, index=True, primary_key=True
    )
    product_id: Mapped[str] = mapped_column(ForeignKey("product.id"), nullable=False, index=True, primary_key=True)
    currency_id: Mapped[str] = mapped_column(ForeignKey("currency.id"), nullable=False, index=True, primary_key=True)

    amount: Mapped[Decimal] = mapped_column(nullable=False, primary_key=True)

    product: Mapped["ProductModel"] = relationship()
    currency: Mapped["CurrencyModel"] = relationship()

    def to_domain(self) -> OfferItem:
        product = self.product.to_domain()
        currency = self.currency.to_domain()
        value = Money(currency=currency, amount=Decimal(self.amount))
        return OfferItem(product=product, value=value)

    @classmethod
    def from_domain(cls, entity: OfferItem, **kwargs: str) -> Self:
        return cls(
            opportunity_id=kwargs["opportunity_id"],
            product_id=kwargs["product_id"],
            currency_id=kwargs["currency_id"],
            amount=entity.value.amount,
        )


class OpportunityNoteModel(BaseNoteModel):
    __tablename__ = "opportunity_note"

    opportunity_id: Mapped[str] = mapped_column(
        ForeignKey("opportunity.id"),
        nullable=False,
        index=True,
        primary_key=True,
    )

    opportunity: Mapped["OpportunityModel"] = relationship(back_populates="notes")

    @classmethod
    def from_domain(cls, entity: Note, **kwargs: Any) -> Self:
        return cls(
            opportunity_id=kwargs["opportunity_id"],
            created_by_id=entity.created_by_id,
            created_at=entity.created_at,
            content=entity.content,
        )


class OpportunityModel(Base[Opportunity]):
    __tablename__ = "opportunity"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    created_by_id: Mapped[str] = mapped_column(nullable=False)
    customer_id: Mapped[str] = mapped_column(nullable=False)
    owner_id: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(nullable=False)
    source_name: Mapped[str] = mapped_column(nullable=False)
    stage_name: Mapped[str] = mapped_column(nullable=False)
    priority_level: Mapped[str] = mapped_column(nullable=False)

    notes: Mapped[list["OpportunityNoteModel"]] = relationship(back_populates="opportunity")
    offer_items: Mapped[list["OfferItemModel"]] = relationship(
        backref="opportunity", cascade="all, delete, delete-orphan"
    )

    @hybrid_property
    def stage(self) -> SimpleNamespace:
        return SimpleNamespace(name=self.stage_name)

    @hybrid_property
    def priority(self) -> SimpleNamespace:
        return SimpleNamespace(level=self.priority_level)

    def to_domain(self) -> Opportunity:
        source = AcquisitionSource(name=self.source_name)
        stage = OpportunityStage(name=self.stage_name)
        priority = Priority(level=self.priority_level)
        offer = tuple(item.to_domain() for item in self.offer_items)
        notes = Notes(history=tuple(note.to_domain() for note in self.notes))

        return Opportunity.reconstitute(
            id=self.id,
            created_by_id=self.created_by_id,
            customer_id=self.customer_id,
            owner_id=self.owner_id,
            created_at=self.created_at,
            source=source,
            stage=stage,
            priority=priority,
            offer=offer,
            notes=notes,
        )

    @classmethod
    def from_domain(cls, entity: Opportunity, **kwargs: Any) -> Self:
        return cls(
            id=entity.id,
            created_by_id=entity.created_by_id,
            customer_id=entity.customer_id,
            owner_id=entity.owner_id,
            source_name=entity.source.name,
            stage_name=entity.stage.name,
            priority_level=entity.priority.level,
        )
