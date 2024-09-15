from abc import ABC, abstractmethod
from typing import Self
from pydantic import BaseModel


class BaseReadModel[Model](ABC, BaseModel):
    @classmethod
    @abstractmethod
    def from_domain(cls, entity: Model) -> Self: ...


class NestedReadModel(BaseModel):
    @classmethod
    def get_examples(cls) -> dict:
        schema = cls.model_json_schema()
        properties = schema.get("properties", {})
        return {key: val.get("examples", [""])[0] for key, val in properties.items()}
