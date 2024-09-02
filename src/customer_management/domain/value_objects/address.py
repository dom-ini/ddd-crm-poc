from attrs import define
from customer_management.domain.value_objects.country import Country
from building_blocks.domain.value_object import ValueObject


@define(frozen=True, kw_only=True)
class Address(ValueObject):
    country: Country
    street: str
    street_no: str
    postal_code: str
    city: str

    def __str__(self) -> str:
        return f"({self.country.code}) {self.street} {self.street_no}, {self.postal_code} {self.city}"
