from typing import TypeVar

from attrs import Attribute

from building_blocks.domain.validators import AllowedValues, ValueT, validate_value_in

ModelT = TypeVar("ModelT")


def attrs_value_in(allowed_values: AllowedValues):
    def validator(_instance: ModelT, _attribute: Attribute, value: ValueT):
        return validate_value_in(value=value, allowed_values=allowed_values)

    return validator
