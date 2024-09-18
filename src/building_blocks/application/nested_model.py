from pydantic import BaseModel


class NestedModel(BaseModel):
    @classmethod
    def get_examples(cls) -> dict:
        schema = cls.model_json_schema()
        properties = schema.get("properties", {})
        return {key: val.get("examples", [""])[0] for key, val in properties.items()}
