from collections.abc import Iterable
from pathlib import Path

from building_blocks.infrastructure.file.io import get_read_db
from building_blocks.infrastructure.vo_service import ReadModelT, ValueObjectService


class FileValueObjectService(ValueObjectService):
    def __init__(self, file_path: Path, read_model: type[ReadModelT]) -> None:
        self._file_path = file_path
        self.read_model = read_model

    def get_all(self) -> Iterable[ReadModelT]:
        with get_read_db(self._file_path) as db:
            print(dict(db))
            all_ids = db.keys()
            value_objects = tuple(self.read_model.from_domain(db.get(id)) for id in all_ids)
        return value_objects
