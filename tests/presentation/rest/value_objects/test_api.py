import pytest
from fastapi import status
from fastapi.testclient import TestClient

from customer_management.domain.value_objects.country import Country
from customer_management.domain.value_objects.language import Language
from sales.domain.value_objects.money.currency import Currency
from sales.domain.value_objects.product import Product

pytestmark = pytest.mark.integration


def test_get_all_countries(client: TestClient, country: Country) -> None:
    r = client.get("/countries")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert result[0].get("code") == country.code
    assert result[0].get("name") == country.name


def test_get_all_languages(client: TestClient, language: Language) -> None:
    r = client.get("/languages")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert result[0].get("code") == language.code
    assert result[0].get("name") == language.name


def test_get_all_currencies(client: TestClient, currency: Currency) -> None:
    r = client.get("/currencies")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert result[0].get("iso_code") == currency.iso_code
    assert result[0].get("name") == currency.name


def test_get_all_products(client: TestClient, product_1: Product, product_2: Product) -> None:
    r = client.get("/products")
    result = r.json()

    fetched_product_names = [product.get("name") for product in result]
    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 2
    assert product_1.name in fetched_product_names
    assert product_2.name in fetched_product_names


@pytest.mark.parametrize(
    "url,method",
    [
        ("/countries", "get"),
        ("/languages", "get"),
        ("/currencies", "get"),
        ("/products", "get"),
    ],
)
def test_calling_vo_endpoints_by_guest_should_fail(client: TestClient, url: str, method: str) -> None:
    r = getattr(client, method)(url, headers={"Authorization": ""})

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
