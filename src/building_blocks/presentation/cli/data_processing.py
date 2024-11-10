from collections.abc import Iterable, Mapping
from datetime import datetime
from numbers import Number

from pydantic import BaseModel

from building_blocks.domain.utils.date import DEFAULT_DATE_FORMAT


def flatten_model_data(model: BaseModel) -> Iterable:
    flat_data: list[str] = []

    def _flatten(item: Mapping | Iterable | datetime | Number) -> None:
        if isinstance(item, Mapping):
            for value in item.values():
                _flatten(value)
        elif isinstance(item, Iterable) and not isinstance(item, str):
            for value in item:
                _flatten(value)
        elif isinstance(item, datetime):
            flat_data.append(item.strftime(DEFAULT_DATE_FORMAT))
        else:
            flat_data.append(str(item))

    _flatten(list(model.model_dump().values()))
    return flat_data


def transform_data(data: Iterable[BaseModel]) -> Iterable:
    return [flatten_model_data(row) for row in data]
