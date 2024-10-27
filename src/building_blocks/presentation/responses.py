from typing import Any

from pydantic import BaseModel


class BasicErrorResponse(BaseModel):
    detail: str


class UnprocessableEntityErrorDetails(BaseModel):
    msg: str
    type: str | None = None
    loc: tuple[int | str, ...] | None = None
    input: Any


class UnprocessableEntityResponse(BaseModel):
    detail: list[UnprocessableEntityErrorDetails]
