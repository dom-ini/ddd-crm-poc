from abc import ABC, abstractmethod
from typing import Self

from pydantic import BaseModel


class BaseReadModel[Model](ABC, BaseModel):
    @classmethod
    @abstractmethod
    def from_domain(cls, entity: Model) -> Self: ...
