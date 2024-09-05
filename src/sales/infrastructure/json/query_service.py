from typing import Callable, Generator, Generic, TypeVar

from building_blocks.application.query_model import BaseReadModel
from building_blocks.infrastructure.dto import BaseDTO
from building_blocks.infrastructure.utils.json import load_json_data

DTOType = TypeVar("DTOType", bound=BaseDTO)
ReadModel = TypeVar("ReadModel", bound=BaseReadModel)


class BaseJsonQueryService(Generic[DTOType, ReadModel]):
    def __init__(self, dto_class: DTOType) -> None:
        self._data: list[DTOType]
        self._dto_class = dto_class

    def _get_dto_data(
        self, filter_func: Callable[[DTOType], bool]
    ) -> Generator[DTOType, None, None]:
        return (item for item in self._data if filter_func(item))

    def _get_read_data(
        self, filter_func: Callable[[DTOType], bool]
    ) -> Generator[ReadModel, None, None]:
        return (item.to_read_model() for item in self._data if filter_func(item))

    def _load_data_from_file(self, file_path: str) -> None:
        raw_data = load_json_data(file_path)
        data = [self._dto_class(**item) for item in raw_data]
        self._data = data
