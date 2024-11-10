from collections.abc import Iterator
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from authentication.infrastructure.service.base import UserReadModel
from authentication.infrastructure.service.firebase import FirebaseUserReadModel
from containers.container import ApplicationContainer
from entrypoints.rest import app as main_app, bind_container
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel


@pytest.fixture(scope="session")
def user(user_data: dict) -> UserReadModel:
    return FirebaseUserReadModel.from_token_data(user_data)


@pytest.fixture(scope="session")
def auth_headers() -> dict:
    return {"Authorization": "Bearer some token"}


@pytest.fixture(scope="session")
def mock_auth_service(testing_container: ApplicationContainer) -> MagicMock:
    return testing_container.auth_service


@pytest.fixture()
def change_user_salesman_id(
    mock_auth_service: MagicMock,
    representative_3: SalesRepresentativeReadModel,
) -> Iterator[None]:
    old_user = mock_auth_service.verify_token.return_value
    new_user = FirebaseUserReadModel.from_token_data(
        {"uid": "some id", "salesman_id": representative_3.id, "roles": []}
    )
    mock_auth_service.verify_token.return_value = new_user
    yield
    mock_auth_service.verify_token.return_value = old_user


@pytest.fixture()
def set_user_admin(mock_auth_service: MagicMock) -> Iterator[None]:
    mock_auth_service.has_role.return_value = True
    yield
    mock_auth_service.has_role.return_value = False


@pytest.fixture(scope="session")
def client(testing_container: ApplicationContainer, auth_headers: dict) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(main_app.router)
    bind_container(app, testing_container)

    client = TestClient(app, headers=auth_headers)
    yield client
