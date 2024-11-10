from abc import ABC, abstractmethod
from types import GenericAlias
from typing import Any, Iterable, cast, get_args, get_origin

from pydantic import BaseModel
from rich.console import Console, ConsoleRenderable
from rich.table import Table


class Renderer(ABC):
    @abstractmethod
    def as_table(self, data: Iterable[Iterable], headers: Iterable[str] | None = None) -> None: ...


class RichRenderer:
    def __init__(self) -> None:
        self._console = Console()

    def as_table(self, data: Iterable[Iterable], headers: Iterable[str] | None = None) -> None:
        table = Table(show_lines=True)
        if headers:
            add_headers_to_table(table, headers)
        populate_table(table, data)

        self._render(table)

    def _render(self, to_render: ConsoleRenderable) -> None:
        self._console.print(to_render)


def add_headers_to_table(table: Table, headers: Iterable[str]) -> None:
    for header in headers:
        table.add_column(header, overflow="fold")


def populate_table(table: Table, data: Iterable[Iterable]) -> None:
    for row in data:
        table.add_row(*row)


def _prettify_header(text: str) -> str:
    return text.replace("_", " ")


def _is_generic_iterable(type_: type[Any] | None) -> bool:
    if not isinstance(type_, GenericAlias):
        return False
    origin_type = get_origin(type_)
    return origin_type is not None and issubclass(origin_type, Iterable)


def _is_nested_model(type_: type[Any] | None) -> bool:
    return isinstance(type_, type) and issubclass(type_, BaseModel)


def _get_nested_model_from_generic(annotation: GenericAlias) -> type[BaseModel]:
    return get_args(annotation)[0]


def get_headers_from_model(model_cls: type[BaseModel], prefix: str = "") -> Iterable[str]:
    def get_field_header(field_name: str) -> str:
        return f"{prefix} - {_prettify_header(field_name)}" if prefix else _prettify_header(field_name)

    headers: list[str] = []
    for field_name, field_info in model_cls.model_fields.items():
        current_field_name = get_field_header(field_name)

        if _is_generic_iterable(field_info.annotation):
            generic = cast(GenericAlias, field_info.annotation)
            nested_type = _get_nested_model_from_generic(generic)
            headers.extend(get_headers_from_model(nested_type, prefix=current_field_name))
        elif _is_nested_model(field_info.annotation):
            model_type = cast(type[BaseModel], field_info.annotation)
            headers.extend(get_headers_from_model(model_type, prefix=current_field_name))
        else:
            headers.append(current_field_name)

    return headers
