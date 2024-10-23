from collections.abc import Iterable
from typing import TypeVar

from sqlalchemy import select

from building_blocks.infrastructure.sql.db import Base, SessionFactory
from building_blocks.infrastructure.vo_service import ReadModelT, ValueObjectService

VOModelT = TypeVar("VOModelT", bound=Base)


class SQLValueObjectService(ValueObjectService):
    def __init__(self, session_factory: SessionFactory, model: type[VOModelT], read_model: type[ReadModelT]) -> None:
        self._session_factory = session_factory
        self.model = model
        self.read_model = read_model

    def get_all(self) -> Iterable[ReadModelT]:
        query = select(self.model)
        with self._session_factory() as db:
            value_objects = tuple(vo.to_domain() for vo in db.scalars(query))
        return tuple(self.read_model.from_domain(vo) for vo in value_objects)
