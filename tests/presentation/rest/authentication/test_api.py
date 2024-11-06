from collections.abc import Iterator
from unittest.mock import MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from authentication.infrastructure.exceptions import AccountDisabled, InvalidToken
from authentication.infrastructure.service.base import UserReadModel
from building_blocks.infrastructure.exceptions import ServerError

pytestmark = pytest.mark.integration


@pytest.fixture()
def set_auth_service_side_effect(mock_auth_service: MagicMock, request: pytest.FixtureRequest) -> Iterator[MagicMock]:
    mock_auth_service.verify_token.side_effect = request.param
    yield mock_auth_service
    mock_auth_service.reset_mock(side_effect=True)


def test_get_current_user_data(client: TestClient, user: UserReadModel) -> None:
    r = client.get("/auth/users/me")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert result.get("id") == user.id
    assert result.get("salesman_id") == user.salesman_id
    assert result.get("roles") == user.roles


def test_get_current_user_data_with_no_token_should_fail(client: TestClient) -> None:
    r = client.get("/auth/users/me", headers={"Authorization": ""})

    assert r.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "set_auth_service_side_effect,http_exception",
    [
        (InvalidToken, status.HTTP_401_UNAUTHORIZED),
        (AccountDisabled, status.HTTP_403_FORBIDDEN),
        (ServerError, status.HTTP_500_INTERNAL_SERVER_ERROR),
    ],
    indirect=["set_auth_service_side_effect"],
)
@pytest.mark.usefixtures("set_auth_service_side_effect")
def test_get_current_user_data_with_invalid_token_should_fail(client: TestClient, http_exception: int) -> None:
    r = client.get("/auth/users/me")

    assert r.status_code == http_exception
