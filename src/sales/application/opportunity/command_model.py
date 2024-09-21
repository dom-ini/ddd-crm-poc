from decimal import Decimal

from faker import Faker
from pydantic import Field

from building_blocks.application.command_model import BaseCommandModel
from building_blocks.application.nested_model import NestedModel
from sales.domain.value_objects.acquisition_source import ALLOWED_SOURCE_NAMES
from sales.domain.value_objects.opportunity_stage import ALLOWED_OPPORTUNITY_STAGES
from sales.domain.value_objects.priority import ALLOWED_PRIORITY_LEVELS

faker = Faker(locale="pl_PL")


class ProductCreateUpdateModel(BaseCommandModel, NestedModel):
    name: str = Field(examples=[faker.catch_phrase()])


class CurrencyCreateUpdateModel(BaseCommandModel, NestedModel):
    name: str = Field(examples=[faker.currency_name()])
    iso_code: str = Field(examples=[faker.currency_code()])


class MoneyCreateUpdateModel(BaseCommandModel, NestedModel):
    currency: CurrencyCreateUpdateModel = Field(examples=[CurrencyCreateUpdateModel.get_examples()])
    amount: Decimal = Field(examples=[faker.pydecimal(left_digits=3, right_digits=2, positive=True)])


class OfferItemCreateUpdateModel(BaseCommandModel, NestedModel):
    product: ProductCreateUpdateModel = Field(examples=[ProductCreateUpdateModel.get_examples()])
    value: MoneyCreateUpdateModel = Field(examples=[MoneyCreateUpdateModel.get_examples()])


class OpportunityCreateModel(BaseCommandModel):
    customer_id: str = Field(examples=[faker.uuid4()])
    source: str = Field(examples=ALLOWED_SOURCE_NAMES)
    priority: str = Field(examples=ALLOWED_PRIORITY_LEVELS)
    offer: list[OfferItemCreateUpdateModel] = Field(examples=[[OfferItemCreateUpdateModel.get_examples()]])


class OpportunityUpdateModel(BaseCommandModel):
    source: str | None = Field(default=None, examples=ALLOWED_SOURCE_NAMES)
    priority: str | None = Field(default=None, examples=ALLOWED_PRIORITY_LEVELS)
    stage: str | None = Field(default=None, examples=ALLOWED_OPPORTUNITY_STAGES)
