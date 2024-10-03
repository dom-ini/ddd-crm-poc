from abc import ABC, abstractmethod

from faker import Faker
from pydantic import BaseModel, EmailStr, Field

from authentication.infrastructure.roles import UserRole

faker = Faker(locale="pl_PL")


class UserReadModel(BaseModel):
    id: str = Field(examples=[faker.uuid4()])
    salesman_id: str | None = Field(examples=[faker.uuid4()])
    roles: list[str] = Field(examples=[[UserRole.ADMIN]])


class UserCreateModel(BaseModel):
    email: EmailStr


class AuthenticationService(ABC):
    @abstractmethod
    def verify_token(self, token: str) -> UserReadModel: ...

    @abstractmethod
    def has_role(self, user_data: UserReadModel, role: str) -> bool: ...

    @abstractmethod
    def create_account(self, email: str, salesman_id: str) -> None: ...
