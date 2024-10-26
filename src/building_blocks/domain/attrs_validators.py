from collections.abc import Callable
from typing import TypeVar

from attrs import Attribute

from building_blocks.domain.validators import AllowedValues, ValueT, validate_value_in

ModelT = TypeVar("ModelT")
Validator = Callable[[ValueT, AllowedValues], None]


def attrs_value_in(allowed_values: AllowedValues) -> Callable[[ModelT, Attribute, ValueT], Validator]:
    def validator(_instance: ModelT, _attribute: Attribute, value: ValueT) -> Validator:
        return validate_value_in(value=value, allowed_values=allowed_values)

    return validator
