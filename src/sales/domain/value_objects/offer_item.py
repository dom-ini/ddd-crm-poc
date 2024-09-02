from attrs import define

from building_blocks.domain.value_object import ValueObject
from sales.domain.value_objects.money.money import Money
from sales.domain.value_objects.product import Product


@define(frozen=True, kw_only=True)
class OfferItem(ValueObject):
    product: Product
    value: Money

    def __str__(self) -> str:
        return f'Offer for: "{self.product}", value: {self.value}'
