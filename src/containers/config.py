import os
from enum import Enum

from containers.container import ApplicationContainer
from containers.file import FileApplicationContainer
from containers.sql import SQLApplicationContainer

PERSISTENCE_ENGINE = os.getenv("PERSISTENCE_ENGINE")


class PersistenceEngine(str, Enum):
    FILE = "FILE"
    SQL = "SQL"


_container_factory = {
    PersistenceEngine.FILE.value: FileApplicationContainer,
    PersistenceEngine.SQL.value: SQLApplicationContainer,
}


class ContainerManager:
    _factory: dict[str, ApplicationContainer] = _container_factory

    @classmethod
    def build(cls, persistence_engine: str = PERSISTENCE_ENGINE or "") -> ApplicationContainer:
        if persistence_engine not in cls._factory:
            raise ValueError(f"Invalid persistence engine. Must be one of these: {cls._factory.keys()}")
        return cls._factory[persistence_engine]()
