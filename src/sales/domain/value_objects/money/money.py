from decimal import Decimal

from attrs import define
from building_blocks.domain.value_object import ValueObject
from sales.domain.value_objects.money.currency import Currency


@define(frozen=True, kw_only=True)
class Money(ValueObject):
    currency: Currency
    amount: Decimal

    def __str__(self) -> str:
        return f"{self.amount} {self.currency.iso_code}"
