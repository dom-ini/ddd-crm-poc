from typing import Self

import firebase_admin
from firebase_admin import auth, credentials
from firebase_admin.exceptions import FirebaseError

from authentication.infrastructure.exceptions import (
    AccountDisabled,
    AuthenticationServiceFailed,
    InvalidToken,
    InvalidUserCreationData,
)
from authentication.infrastructure.service.base import AuthenticationService, UserReadModel
from building_blocks.infrastructure.exceptions import ServerError


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
        except (
            ValueError,
            auth.InvalidIdTokenError,
            auth.ExpiredIdTokenError,
            auth.RevokedIdTokenError,
        ) as e:
            raise InvalidToken from e
        except auth.UserDisabledError as e:
            raise AccountDisabled from e
        except auth.CertificateFetchError as e:
            raise ServerError from e
        return FirebaseUserReadModel.from_token_data(data)

    def has_role(self, user_data: FirebaseUserReadModel, role: str) -> bool:
        roles = user_data.roles
        if not roles:
            return False
        return role in roles

    def create_account(self, email: str, salesman_id: str) -> None:
        try:
            new_user = auth.create_user(email=email)
            auth.set_custom_user_claims(new_user.uid, {"salesman_id": salesman_id})
        except ValueError as e:
            raise InvalidUserCreationData from e
        except FirebaseError as e:
            raise AuthenticationServiceFailed from e
