from attrs import define, field, Attribute
from building_blocks.domain.validators import validate_email, validate_phone
from building_blocks.domain.value_object import ValueObject
from sales.domain.exceptions import EmailOrPhoneNumberShouldBeSet


@define(frozen=True, kw_only=True)
class ContactData(ValueObject):
    first_name: str
    last_name: str
    company_name: str
    phone: str | None = field(default=None)
    email: str | None = field(default=None)

    @phone.validator
    def _validate_phone(self, _attribute: Attribute, value: str) -> None:
        if value is not None:
            validate_phone(value)

    @email.validator
    def _validate_email(self, _attribute: Attribute, value: str) -> None:
        if value is not None:
            validate_email(value)

    def __attrs_post_init__(self) -> None:
        if not self.phone and not self.email:
            raise EmailOrPhoneNumberShouldBeSet

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} ({self.company_name})"
