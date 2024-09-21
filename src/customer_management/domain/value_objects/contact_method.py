from typing import Callable, Literal, get_args

from attrs import Attribute, define, field

from building_blocks.domain.attrs_validators import attrs_value_in
from building_blocks.domain.validators import validate_email, validate_phone
from building_blocks.domain.value_object import ValueObject

ContactMethodType = Literal["email", "phone"]
ValidatorType = Callable[[str], None]
ValidatorFactory = dict[ContactMethodType, ValidatorType]

ALLOWED_CONTACT_TYPES = get_args(ContactMethodType)
VALIDATION_STRATEGIES: ValidatorFactory = {
    "phone": validate_phone,
    "email": validate_email,
}


@define(frozen=True, kw_only=True)
class ContactMethod(ValueObject):
    type: ContactMethodType = field(validator=attrs_value_in(ALLOWED_CONTACT_TYPES))
    value: str = field()
    is_preferred: bool = field(default=False)

    @value.validator
    def _validate_value(self, _attribute: Attribute, value: str) -> None:
        contact_type = self.type
        validator = self.get_validators()[contact_type]
        validator(value)

    @staticmethod
    def get_validators() -> ValidatorFactory:
        return VALIDATION_STRATEGIES

    def __str__(self) -> str:
        preferred_suffix = " (preferred)" if self.is_preferred else ""
        return f"{self.type}={self.value}" + preferred_suffix
