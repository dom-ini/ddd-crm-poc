from typing import TypeVar

from attrs import Attribute

from building_blocks.domain.validators import (
    AllowedValues,
    ValueType,
    validate_value_in,
)

ModelType = TypeVar("Model")


def attrs_value_in(allowed_values: AllowedValues):
    def validator(_instance: ModelType, _attribute: Attribute, value: ValueType):
        return validate_value_in(value=value, allowed_values=allowed_values)

    return validator
