import random

from pydantic import BaseModel


class NestedModel(BaseModel):
    @classmethod
    def get_examples(cls) -> dict:
        schema = cls.model_json_schema()
        properties = schema.get("properties", {})
        return {key: random.choice(val.get("examples", [""])) for key, val in properties.items()}
