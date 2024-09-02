from typing import Any, Callable, Iterable, TypeVar
import email_validator as ev
import phonenumbers
from building_blocks.domain.exceptions import (
    DuplicateEntry,
    InvalidEmailAddress,
    InvalidPhoneNumber,
    ValueNotAllowed,
)
from building_blocks.domain.utils.iterables import get_duplicates


ValueType = TypeVar("Value")
AllowedValues = Iterable[ValueType]
GetDuplicatesCallback = Callable[[ValueType], Any]


def validate_no_duplicates(
    value: ValueType, callback: GetDuplicatesCallback = lambda x: x
) -> None:
    duplicates = get_duplicates(value, callback)
    if duplicates:
        raise DuplicateEntry(duplicates)


def validate_value_in(value: ValueType, allowed_values: AllowedValues) -> None:
    if value not in allowed_values:
        raise ValueNotAllowed(value=value, allowed_values=allowed_values)


def validate_email(email: str) -> None:
    try:
        ev.validate_email(email, check_deliverability=False)
    except ev.EmailNotValidError as base_exc:
        raise InvalidEmailAddress(email) from base_exc


def validate_phone(phone_no: str) -> None:
    try:
        parsed_no = phonenumbers.parse(phone_no)
    except phonenumbers.NumberParseException as base_exc:
        raise InvalidPhoneNumber(phone_no) from base_exc
    is_valid = phonenumbers.is_valid_number(parsed_no)
    if not is_valid:
        raise InvalidPhoneNumber(phone_no)
