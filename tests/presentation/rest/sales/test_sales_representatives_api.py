from collections.abc import Iterator
from unittest.mock import ANY, MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from authentication.infrastructure.exceptions import InvalidUserCreationData
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel

pytestmark = pytest.mark.integration


@pytest.fixture()
def set_create_account_error(mock_auth_service: MagicMock) -> Iterator[None]:
    mock_auth_service.create_account.side_effect = InvalidUserCreationData
    yield
    mock_auth_service.create_account.side_effect = None


@pytest.mark.usefixtures("set_user_admin", "representative_1", "representative_2", "representative_3")
def test_get_sales_representatives(client: TestClient) -> None:
    r = client.get("/sales-representatives")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 3


@pytest.mark.usefixtures("set_user_admin")
def test_create_sales_representative(client: TestClient, mock_auth_service: MagicMock) -> None:
    data = {
        "salesman_data": {"first_name": "Iks", "last_name": "Iksiński"},
        "user_data": {"email": "salesrep@example.com"},
    }

    r = client.post("/sales-representatives", json=data)
    result = r.json()

    assert result.get("first_name") == data["salesman_data"]["first_name"]
    assert result.get("last_name") == data["salesman_data"]["last_name"]
    mock_auth_service.create_account.assert_called_once_with(email=data["user_data"]["email"], salesman_id=ANY)


@pytest.mark.usefixtures("set_user_admin", "set_create_account_error")
def test_create_sales_representative_with_invalid_data_should_fail(
    client: TestClient, mock_auth_service: MagicMock
) -> None:
    mock_auth_service.create_account
    data = {
        "salesman_data": {"first_name": "Iks", "last_name": "Iksiński"},
        "user_data": {"email": "salesrep@example.com"},
    }

    r = client.post("/sales-representatives", json=data)

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("set_user_admin", "change_user_salesman_id")
def test_update_sales_representative(client: TestClient, representative_3: SalesRepresentativeReadModel) -> None:
    data = {"first_name": "Nowicjusz", "last_name": "Nowiński"}

    r = client.put(f"/sales-representatives/{representative_3.id}", json=data)
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert result.get("first_name") == data["first_name"]
    assert result.get("last_name") == data["last_name"]


@pytest.mark.usefixtures("set_user_admin")
def test_update_sales_representative_by_other_user_should_fail(
    client: TestClient, representative_3: SalesRepresentativeReadModel
) -> None:
    r = client.put(f"/sales-representatives/{representative_3.id}", json={"first_name": "Nowicjusz"})

    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.usefixtures("set_user_admin")
def test_update_sales_representative_with_invalid_id_should_fail(client: TestClient) -> None:
    r = client.put("/sales-representatives/invalid", json={"first_name": "Nowicjusz"})

    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "url,method",
    [
        ("/sales-representatives", "get"),
        ("/sales-representatives", "post"),
    ],
)
def test_calling_admin_endpoint_by_non_admin_should_fail(client: TestClient, url: str, method: str) -> None:
    r = getattr(client, method)(url)

    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "url,method",
    [
        ("/sales-representatives", "get"),
        ("/sales-representatives", "post"),
        ("/sales-representatives/representative_id", "put"),
    ],
)
def test_calling_leads_endpoints_by_guest_should_fail(client: TestClient, url: str, method: str) -> None:
    r = getattr(client, method)(url, headers={"Authorization": ""})

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
