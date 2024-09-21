from collections.abc import Iterable
from typing import Any


class DomainException(Exception):
    message: str

    def __init__(self) -> None:
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class InvalidInput(DomainException):
    input_type: str

    def __init__(self, value: Any) -> None:
        self.message = f'Invalid {self.input_type}: "{value}"'
        super().__init__()


class InvalidPhoneNumber(InvalidInput):
    input_type = "phone"


class InvalidEmailAddress(InvalidInput):
    input_type = "email"


class ValueNotAllowed(DomainException):
    def __init__(self, value: Any, allowed_values: Iterable[Any]) -> None:
        self.message = f'Invalid value: "{value}", should be one of these: {allowed_values}'
        super().__init__()


class DuplicateEntry(DomainException):
    def __init__(self, duplicates: tuple) -> None:
        duplicates_info = "\n".join(str(entry) for entry in duplicates)
        self.message = f"Duplicate entries found:\n{duplicates_info}"
        super().__init__()
