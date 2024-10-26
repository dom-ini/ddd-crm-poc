from unittest.mock import MagicMock

import pytest
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
from pytest_mock import MockerFixture

from authentication.infrastructure.exceptions import (
    AccountDisabled,
    AuthenticationServiceFailed,
    InvalidToken,
    InvalidUserCreationData,
)
from authentication.infrastructure.roles import UserRole
from authentication.infrastructure.service.base import AuthenticationService
from authentication.infrastructure.service.firebase import FirebaseAuthenticationService, FirebaseUserReadModel
from building_blocks.infrastructure.exceptions import ServerError


@pytest.fixture(autouse=True)
def mock_initialize_app(mocker: MockerFixture) -> None:
    mocker.patch("firebase_admin.initialize_app")


@pytest.fixture()
def mock_verify_token(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("firebase_admin.auth.verify_id_token")


@pytest.fixture()
def mock_create_user(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("firebase_admin.auth.create_user")


@pytest.fixture()
def mock_set_user_claims(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("firebase_admin.auth.set_custom_user_claims")


@pytest.fixture()
def auth_service() -> AuthenticationService:
    return FirebaseAuthenticationService(credentials=object())


@pytest.mark.parametrize(
    "firebase_exception,exception",
    [
        (auth.InvalidIdTokenError(""), InvalidToken),
        (auth.UserDisabledError(""), AccountDisabled),
        (auth.CertificateFetchError("", ""), ServerError),
    ],
)
def test_verify_token_raises_correct_exception(
    firebase_exception: Exception,
    exception: Exception,
    auth_service: AuthenticationService,
    mock_verify_token: MagicMock,
) -> None:
    mock_verify_token.side_effect = firebase_exception

    with pytest.raises(exception):
        auth_service.verify_token("token")


def test_verify_token_returns_user_model_on_successful_verification(
    auth_service: AuthenticationService,
    mock_verify_token: MagicMock,
) -> None:
    uid = "uid"
    roles = [UserRole.ADMIN.value]
    salesman_id = "salesman_id"
    mock_verify_token.return_value = {"uid": uid, "roles": roles, "salesman_id": salesman_id}

    user = auth_service.verify_token("token")

    assert user.id == uid
    assert user.roles[0] == roles[0]
    assert user.salesman_id == salesman_id


@pytest.mark.parametrize(
    "user_roles,role,result",
    [
        ([UserRole.ADMIN.value], UserRole.ADMIN.value, True),
        ([], UserRole.ADMIN.value, False),
        ([UserRole.ADMIN.value], "other role", False),
    ],
)
def test_has_role(auth_service: AuthenticationService, user_roles: list[str], role: str, result: bool) -> None:
    user = FirebaseUserReadModel(id="id", roles=user_roles, salesman_id="salesman id")

    assert auth_service.has_role(user_data=user, role=role) is result


@pytest.mark.parametrize(
    "firebase_exception,exception",
    [(ValueError, InvalidUserCreationData), (FirebaseError("", ""), AuthenticationServiceFailed)],
)
@pytest.mark.usefixtures("mock_set_user_claims")
def test_create_account_raises_correct_exception_on_user_creation_error(
    auth_service: AuthenticationService,
    mock_create_user: MagicMock,
    firebase_exception: Exception,
    exception: Exception,
) -> None:
    mock_create_user.side_effect = firebase_exception

    with pytest.raises(exception):
        auth_service.create_account(email="email", salesman_id="salesman_id")


@pytest.mark.parametrize(
    "firebase_exception,exception",
    [(ValueError, InvalidUserCreationData), (FirebaseError("", ""), AuthenticationServiceFailed)],
)
@pytest.mark.usefixtures("mock_create_user")
def test_create_account_raises_correct_exception_on_setting_user_claims_error(
    auth_service: AuthenticationService,
    mock_set_user_claims: MagicMock,
    firebase_exception: Exception,
    exception: Exception,
) -> None:
    mock_set_user_claims.side_effect = firebase_exception

    with pytest.raises(exception):
        auth_service.create_account(email="email", salesman_id="salesman_id")
