from pydantic import BaseModel


class UserReadModel(BaseModel):
    id: str
    salesman_id: str | None
