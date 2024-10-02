from abc import ABC, abstractmethod

from pydantic import BaseModel


class UserReadModel(BaseModel):
    id: str
    salesman_id: str | None
    roles: list[str]


class AuthenticationService(ABC):
    @abstractmethod
    def verify_token(self, token: str) -> UserReadModel: ...

    @abstractmethod
    def has_role(self, user_data: UserReadModel, role: str) -> bool: ...
