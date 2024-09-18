from decimal import Decimal

from attr import Attribute
from attrs import define, field
from building_blocks.domain.value_object import ValueObject
from sales.domain.exceptions import AmountMustBeGreaterThanZero
from sales.domain.value_objects.money.currency import Currency


@define(frozen=True, kw_only=True)
class Money(ValueObject):
    currency: Currency
    amount: Decimal = field()

    @amount.validator
    def _validate_amount(self, _attribute: Attribute, value: Decimal) -> None:
        if value <= 0:
            raise AmountMustBeGreaterThanZero

    def __str__(self) -> str:
        return f"{self.amount} {self.currency.iso_code}"
