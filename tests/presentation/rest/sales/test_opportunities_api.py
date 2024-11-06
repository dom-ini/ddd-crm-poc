import pytest
from fastapi import status
from fastapi.testclient import TestClient

from customer_management.application.query_model import CustomerReadModel
from sales.application.opportunity.query_model import OpportunityReadModel
from sales.domain.value_objects.money.currency import Currency
from sales.domain.value_objects.product import Product

pytestmark = pytest.mark.integration


@pytest.mark.usefixtures("opportunity_1", "opportunity_2", "opportunity_3", "api_opportunity")
def test_get_opportunities_without_filters(client: TestClient) -> None:
    r = client.get("/opportunities")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 4


def test_get_opportunities_with_filters(client: TestClient, opportunity_1: OpportunityReadModel) -> None:
    query_params = {
        "customer_id": opportunity_1.customer_id,
        "owner_id": opportunity_1.owner_id,
        "stage": opportunity_1.stage,
        "priority": opportunity_1.priority,
    }
    url = "/opportunities?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
    r = client.get(url)
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert result[0].get("id") == opportunity_1.id


def test_get_opportunity(client: TestClient, opportunity_1: OpportunityReadModel) -> None:
    r = client.get(f"/opportunities/{opportunity_1.id}")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert result.get("id") == opportunity_1.id


def test_get_opportunity_with_invalid_id_should_fail(client: TestClient) -> None:
    r = client.get("/opportunities/invalid")

    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_get_opportunity_offer(client: TestClient, opportunity_1: OpportunityReadModel, product_1: Product) -> None:
    r = client.get(f"/opportunities/{opportunity_1.id}/offer-items")
    result = r.json()

    assert len(result) == 1
    assert result[0].get("product").get("name") == product_1.name


def test_get_opportunity_offer_with_invalid_id_should_fail(client: TestClient) -> None:
    r = client.get("/opportunities/invalid/offer-items")

    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_get_opportunity_notes(client: TestClient, opportunity_1: OpportunityReadModel, note_content: str) -> None:
    r = client.get(f"/opportunities/{opportunity_1.id}/notes")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert result[0].get("content") == note_content


def test_get_opportunity_notes_with_invalid_id_should_fail(client: TestClient) -> None:
    r = client.get("/opportunities/invalid/notes")

    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("change_user_salesman_id")
def test_create_opportunity(
    client: TestClient, product_1: Product, currency: Currency, customer_1: CustomerReadModel
) -> None:
    data = {
        "customer_id": customer_1.id,
        "source": "ads",
        "priority": "low",
        "offer": [
            {
                "product": {"name": product_1.name},
                "value": {
                    "amount": "123.19",
                    "currency": {
                        "iso_code": currency.iso_code,
                        "name": currency.name,
                    },
                },
            }
        ],
    }

    r = client.post("/opportunities", json=data)
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert result.get("id")


def test_create_opportunity_with_invalid_data_should_fail(client: TestClient) -> None:
    data = {
        "customer_id": "invalid id",
        "source": "invalid",
        "priority": "invalid",
        "offer": [
            {
                "product": {"name": "invalid"},
                "value": {
                    "amount": "123.19",
                    "currency": {
                        "iso_code": "invalid",
                        "name": "invalid",
                    },
                },
            }
        ],
    }

    r = client.post("/opportunities", json=data)

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("change_user_salesman_id")
def test_update_opportunity(client: TestClient, opportunity_1: OpportunityReadModel) -> None:
    data = {"source": "cold call", "priority": "high", "stage": "negotiation"}
    r = client.put(f"/opportunities/{opportunity_1.id}", json=data)
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert result.get("source") == data["source"]
    assert result.get("priority") == data["priority"]
    assert result.get("stage") == data["stage"]


def test_update_opportunity_with_invalid_id_should_fail(client: TestClient) -> None:
    r = client.put("/opportunities/invalid", json={})

    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_update_opportunity_by_non_owner_should_fail(client: TestClient, opportunity_1: OpportunityReadModel) -> None:
    r = client.put(f"/opportunities/{opportunity_1.id}", json={"source": "social media"})

    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.usefixtures("change_user_salesman_id")
def test_update_opportunity_with_invalid_data_should_fail(
    client: TestClient, opportunity_1: OpportunityReadModel
) -> None:
    r = client.put(f"/opportunities/{opportunity_1.id}", json={"source": "invalid"})

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("change_user_salesman_id")
def test_update_opportunity_offer(
    client: TestClient, opportunity_1: OpportunityReadModel, product_2: Product, currency: Currency
) -> None:
    data = [
        {
            "product": {"name": product_2.name},
            "value": {"amount": "378.47", "currency": {"iso_code": currency.iso_code, "name": currency.name}},
        }
    ]

    r = client.put(f"/opportunities/{opportunity_1.id}/offer-items", json=data)
    result = r.json()

    fetched_product = result[0].get("product")
    fetched_value = result[0].get("value")
    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert fetched_product.get("name") == product_2.name
    assert fetched_value.get("amount") == data[0]["value"]["amount"]


def test_update_opportunity_offer_with_invalid_id_should_fail(client: TestClient) -> None:
    r = client.put("/opportunities/invalid/offer-items", json=[])

    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_update_opportunity_offer_by_non_owner_should_fail(
    client: TestClient, opportunity_1: OpportunityReadModel
) -> None:
    r = client.put(f"/opportunities/{opportunity_1.id}/offer-items", json=[])

    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.usefixtures("change_user_salesman_id")
def test_update_opportunity_offer_with_invalid_data_should_fail(
    client: TestClient, opportunity_1: OpportunityReadModel
) -> None:
    data = [
        {
            "product": {"name": "invalid"},
            "value": {"amount": "378.47", "currency": {"iso_code": "invalid", "name": "invalid"}},
        }
    ]
    r = client.put(f"/opportunities/{opportunity_1.id}/offer-items", json=data)

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("change_user_salesman_id")
def test_create_opportunity_note(client: TestClient, opportunity_1: OpportunityReadModel) -> None:
    new_content = "some new content"

    r = client.post(f"/opportunities/{opportunity_1.id}/notes", json={"content": new_content})
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert result.get("content") == new_content


def test_create_opportunity_note_with_invalid_id_should_fail(client: TestClient) -> None:
    r = client.post("/opportunities/invalid/notes", json={"content": "new content"})

    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_create_opportunity_note_by_non_owner_should_fail(
    client: TestClient, opportunity_1: OpportunityReadModel
) -> None:
    r = client.post(f"/opportunities/{opportunity_1.id}/notes", json={"content": "new content"})

    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "url,method",
    [
        ("/opportunities", "get"),
        ("/opportunities", "post"),
        ("/opportunities/opportunity_id", "get"),
        ("/opportunities/opportunity_id", "put"),
        ("/opportunities/opportunity_id/offer-items", "get"),
        ("/opportunities/opportunity_id/offer-items", "put"),
        ("/opportunities/opportunity_id/notes", "get"),
        ("/opportunities/opportunity_id/notes", "post"),
    ],
)
def test_calling_opportunities_endpoints_by_guest_should_fail(client: TestClient, url: str, method: str) -> None:
    r = getattr(client, method)(url, headers={"Authorization": ""})

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
