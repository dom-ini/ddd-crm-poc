import pytest
from fastapi import status
from fastapi.testclient import TestClient

from customer_management.application.query_model import CustomerReadModel
from sales.application.lead.query_model import LeadReadModel
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel

pytestmark = pytest.mark.integration


def test_get_leads_without_filters(client: TestClient) -> None:
    r = client.get("/leads")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 2


def test_get_leads_with_filters(
    client: TestClient, lead_1: LeadReadModel, representative_3: SalesRepresentativeReadModel
) -> None:
    query_params = {
        "customer_id": lead_1.customer_id,
        "salesman_id": representative_3.id,
        "contact_phone": lead_1.contact_data.phone,
        "contact_email": lead_1.contact_data.email.upper(),
    }
    url = "/leads?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
    r = client.get(url)
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert result[0].get("id") == lead_1.id


def test_get_lead(client: TestClient, lead_1: LeadReadModel) -> None:
    r = client.get(f"/leads/{lead_1.id}")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert result.get("id") == lead_1.id


def test_get_lead_with_invalid_id_should_fail(client: TestClient) -> None:
    r = client.get("/leads/invalid")

    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_get_lead_assignments(
    client: TestClient, lead_1: LeadReadModel, representative_3: SalesRepresentativeReadModel
) -> None:
    r = client.get(f"/leads/{lead_1.id}/assignments")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert result[0].get("previous_owner_id") is None
    assert result[0].get("new_owner_id") == representative_3.id


def test_get_lead_assignments_with_invalid_id_should_fail(client: TestClient) -> None:
    r = client.get("/leads/invalid/assignments")

    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_get_lead_notes(client: TestClient, lead_1: LeadReadModel, note_content: str) -> None:
    r = client.get(f"/leads/{lead_1.id}/notes")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert result[0].get("content") == note_content


def test_get_lead_notes_with_invalid_id_should_fail(client: TestClient) -> None:
    r = client.get("/leads/invalid/notes")

    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("change_user_salesman_id")
def test_create_lead(client: TestClient, customer_4: CustomerReadModel) -> None:
    data = {
        "customer_id": customer_4.id,
        "source": "social media",
        "contact_data": {
            "email": "lead1email@example.com",
            "first_name": "Jan",
            "last_name": "Kowalski",
            "phone": "+48321321321",
        },
    }

    r = client.post("/leads", json=data)
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert result.get("id")


def test_create_lead_with_invalid_data_should_fail(client: TestClient) -> None:
    data = {
        "customer_id": "invalid id",
        "source": "invalid",
        "contact_data": {
            "email": "invalid",
            "first_name": "Jan",
            "last_name": "Kowalski",
            "phone": "invalid",
        },
    }

    r = client.post("/leads", json=data)

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("change_user_salesman_id")
def test_update_lead(client: TestClient, lead_1: LeadReadModel) -> None:
    data = {
        "source": "cold call",
        "contact_data": {
            "email": "newleademail@example.com",
            "first_name": "Nowicjusz",
            "last_name": "Nowakowski",
            "phone": "+48123999999",
        },
    }
    r = client.put(f"/leads/{lead_1.id}", json=data)
    result = r.json()

    contact_data = result.get("contact_data")
    assert r.status_code == status.HTTP_200_OK
    assert contact_data.get("email") == data["contact_data"]["email"]
    assert contact_data.get("first_name") == data["contact_data"]["first_name"]
    assert contact_data.get("last_name") == data["contact_data"]["last_name"]
    assert contact_data.get("phone") == data["contact_data"]["phone"]


def test_update_lead_with_invalid_id_should_fail(client: TestClient) -> None:
    r = client.put("/leads/invalid", json={})

    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_update_lead_by_non_owner_should_fail(client: TestClient, lead_1: LeadReadModel) -> None:
    r = client.put(f"/leads/{lead_1.id}", json={"source": "social media"})

    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.usefixtures("change_user_salesman_id")
def test_update_lead_with_invalid_data_should_fail(client: TestClient, lead_1: LeadReadModel) -> None:
    r = client.put(f"/leads/{lead_1.id}", json={"source": "invalid"})

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("change_user_salesman_id")
def test_assign_lead(client: TestClient, lead_2: LeadReadModel, representative_1: SalesRepresentativeReadModel) -> None:
    r = client.post(f"/leads/{lead_2.id}/assignments", json={"new_salesman_id": representative_1.id})
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert result.get("previous_owner_id") is None
    assert result.get("new_owner_id") == representative_1.id


def test_assign_lead_with_invalid_id_should_fail(
    client: TestClient, representative_3: SalesRepresentativeReadModel
) -> None:
    r = client.post("/leads/invalid/assignments", json={"new_salesman_id": representative_3.id})

    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_assign_lead_by_non_owner_should_fail(
    client: TestClient, lead_1: LeadReadModel, representative_1: LeadReadModel
) -> None:
    r = client.post(f"/leads/{lead_1.id}/assignments", json={"new_salesman_id": representative_1.id})

    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.usefixtures("change_user_salesman_id")
def test_assign_lead_with_invalid_data_should_fail(client: TestClient, lead_1: LeadReadModel) -> None:
    r = client.post(f"/leads/{lead_1.id}/assignments", json={"new_salesman_id": "invalid"})

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("change_user_salesman_id")
def test_assign_lead_to_already_assigned_salesman_should_fail(
    client: TestClient, lead_1: LeadReadModel, representative_3: SalesRepresentativeReadModel
) -> None:
    r = client.post(f"/leads/{lead_1.id}/assignments", json={"new_salesman_id": representative_3.id})

    assert r.status_code == status.HTTP_409_CONFLICT


@pytest.mark.usefixtures("change_user_salesman_id")
def test_create_lead_note(client: TestClient, lead_1: LeadReadModel) -> None:
    new_content = "some new content"

    r = client.post(f"/leads/{lead_1.id}/notes", json={"content": new_content})
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert result.get("content") == new_content


def test_create_lead_note_with_invalid_id_should_fail(client: TestClient) -> None:
    r = client.post("/leads/invalid/notes", json={"content": "new content"})

    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_create_lead_note_by_non_owner_should_fail(client: TestClient, lead_1: LeadReadModel) -> None:
    r = client.post(f"/leads/{lead_1.id}/notes", json={"content": "new content"})

    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "url,method",
    [
        ("/leads", "get"),
        ("/leads", "post"),
        ("/leads/lead_id", "get"),
        ("/leads/lead_id", "put"),
        ("/leads/lead_id/assignments", "get"),
        ("/leads/lead_id/assignments", "post"),
        ("/leads/lead_id/notes", "get"),
        ("/leads/lead_id/notes", "post"),
    ],
)
def test_calling_leads_endpoints_by_guest_should_fail(client: TestClient, url: str, method: str) -> None:
    r = getattr(client, method)(url, headers={"Authorization": ""})

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
