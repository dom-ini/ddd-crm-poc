import datetime as dt
from decimal import Decimal
from typing import Self

from faker import Faker
from pydantic import Field

from building_blocks.application.nested_model import NestedModel
from building_blocks.application.query_model import BaseReadModel
from sales.domain.entities.opportunity import Opportunity
from sales.domain.value_objects.acquisition_source import ALLOWED_SOURCE_NAMES
from sales.domain.value_objects.money.currency import Currency
from sales.domain.value_objects.money.money import Money
from sales.domain.value_objects.offer_item import OfferItem
from sales.domain.value_objects.opportunity_stage import ALLOWED_OPPORTUNITY_STAGES
from sales.domain.value_objects.priority import ALLOWED_PRIORITY_LEVELS
from sales.domain.value_objects.product import Product

faker = Faker(locale="pl_PL")


class ProductReadModel(BaseReadModel[Product], NestedModel):
    name: str = Field(examples=[faker.catch_phrase()])

    @classmethod
    def from_domain(cls, entity: Product) -> Self:
        return cls(name=entity.name)


class CurrencyReadModel(BaseReadModel[Currency], NestedModel):
    name: str = Field(examples=[faker.currency_name()])
    iso_code: str = Field(examples=[faker.currency_code()])

    @classmethod
    def from_domain(cls, entity: Currency) -> Self:
        return cls(name=entity.name, iso_code=entity.iso_code)


class MoneyReadModel(BaseReadModel[Money], NestedModel):
    currency: CurrencyReadModel = Field(examples=[CurrencyReadModel.get_examples()])
    amount: Decimal = Field(examples=[faker.pydecimal(left_digits=3, right_digits=2, positive=True)])

    @classmethod
    def from_domain(cls, entity: Money) -> Self:
        return cls(
            currency=CurrencyReadModel.from_domain(entity.currency),
            amount=entity.amount,
        )


class OfferItemReadModel(BaseReadModel[OfferItem], NestedModel):
    product: ProductReadModel = Field(examples=[ProductReadModel.get_examples()])
    value: MoneyReadModel = Field(examples=[MoneyReadModel.get_examples()])

    @classmethod
    def from_domain(cls, entity: OfferItem) -> Self:
        return cls(
            product=ProductReadModel.from_domain(entity.product),
            value=MoneyReadModel.from_domain(entity.value),
        )


class OpportunityReadModel(BaseReadModel[Opportunity]):
    id: str = Field(examples=[faker.uuid4()])
    source: str = Field(examples=ALLOWED_SOURCE_NAMES)
    stage: str = Field(examples=ALLOWED_OPPORTUNITY_STAGES)
    priority: str = Field(examples=ALLOWED_PRIORITY_LEVELS)
    created_by_id: str = Field(examples=[faker.uuid4()])
    customer_id: str = Field(examples=[faker.uuid4()])
    owner_id: str = Field(examples=[faker.uuid4()])
    created_at: dt.datetime = Field(examples=[faker.date_time_this_year()])

    @classmethod
    def from_domain(cls, entity: Opportunity) -> Self:
        return cls(
            id=entity.id,
            source=entity.source.name,
            stage=entity.stage.name,
            priority=entity.priority.level,
            created_by_id=entity.created_by_id,
            customer_id=entity.customer_id,
            owner_id=entity.owner_id,
            created_at=entity.created_at,
        )
