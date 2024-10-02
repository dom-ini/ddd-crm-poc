from typing import Self

import firebase_admin
from firebase_admin import auth, credentials

from authentication.infrastructure.exceptions import InvalidToken
from authentication.infrastructure.service.base import AuthenticationService, UserReadModel


class FirebaseUserReadModel(UserReadModel):
    @classmethod
    def from_token_data(cls, token_data: dict) -> Self:
        user_id = token_data.get("uid")
        roles = token_data.get("roles", [])
        salesman_id = token_data.get("salesman_id")
        return cls(id=user_id, salesman_id=salesman_id, roles=roles)


class FirebaseAuthenticationService(AuthenticationService):
    def __init__(self, credentials: credentials.Certificate) -> None:
        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials)

    def verify_token(self, token: str) -> FirebaseUserReadModel:
        try:
            data = auth.verify_id_token(token)
        except Exception as e:
            raise InvalidToken from e
        return FirebaseUserReadModel.from_token_data(data)

    def has_role(self, user_data: FirebaseUserReadModel, role: str) -> bool:
        roles = user_data.roles
        if not roles:
            return False
        return role in roles
