import pytest
from fastapi import status
from fastapi.testclient import TestClient

from customer_management.application.command import CustomerCommandUseCase
from customer_management.application.command_model import (
    CompanyInfoCreateUpdateModel,
    ContactMethodCreateUpdateModel,
    ContactPersonCreateModel,
    CustomerCreateModel,
    LanguageCreateUpdateModel,
)
from customer_management.application.query_model import ContactPersonReadModel, CustomerReadModel
from customer_management.domain.value_objects.country import Country
from customer_management.domain.value_objects.language import Language
from sales.application.sales_representative.query_model import SalesRepresentativeReadModel

pytestmark = pytest.mark.integration


@pytest.fixture(scope="session", autouse=True)
def api_customer_without_contact_persons(
    customer_command_use_case: CustomerCommandUseCase,
    company_info: CompanyInfoCreateUpdateModel,
    representative_3: SalesRepresentativeReadModel,
) -> CustomerReadModel:
    data = CustomerCreateModel(relation_manager_id=representative_3.id, company_info=company_info)
    customer = customer_command_use_case.create(customer_data=data)
    return customer


@pytest.fixture(scope="session", autouse=True)
def api_customer_with_contact_persons(
    customer_command_use_case: CustomerCommandUseCase,
    company_info: CompanyInfoCreateUpdateModel,
    representative_3: SalesRepresentativeReadModel,
) -> CustomerReadModel:
    data = CustomerCreateModel(relation_manager_id=representative_3.id, company_info=company_info)
    customer = customer_command_use_case.create(customer_data=data)
    return customer


@pytest.fixture(scope="session", autouse=True)
def api_contact_person(
    customer_command_use_case: CustomerCommandUseCase,
    api_customer_with_contact_persons: CustomerReadModel,
    language: Language,
) -> ContactPersonReadModel:
    contact_person_data = ContactPersonCreateModel(
        first_name="Jan",
        last_name="Kowalski",
        job_title="CFO",
        preferred_language=LanguageCreateUpdateModel(name=language.name, code=language.code),
        contact_methods=(
            (ContactMethodCreateUpdateModel(type="email", value="apicustomer@example.com", is_preferred=True)),
        ),
    )
    contact_person = customer_command_use_case.create_contact_person(
        customer_id=api_customer_with_contact_persons.id,
        editor_id=api_customer_with_contact_persons.relation_manager_id,
        data=contact_person_data,
    )
    return contact_person


@pytest.mark.usefixtures(
    "customer_1",
    "customer_2",
    "customer_3",
    "customer_4",
    "api_customer_without_contact_persons",
    "api_customer_without_contact_persons",
    "api_customer_with_open_opportunity",
)
def test_get_customers_without_filters(client: TestClient) -> None:
    r = client.get("/customers")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 7


def test_get_customers_with_filters(client: TestClient, customer_2: CustomerReadModel) -> None:
    query_params = {
        "relation_manager_id": customer_2.relation_manager_id,
        "status": customer_2.status,
        "company_name": customer_2.company_info.name.upper().replace(" ", ""),
        "industry": customer_2.company_info.industry,
        "company_size": customer_2.company_info.size,
        "legal_form": customer_2.company_info.legal_form,
    }
    url = "/customers?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
    r = client.get(url)
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert len(result) == 1
    assert result[0].get("id") == customer_2.id


def test_create_customer(client: TestClient, representative_3: SalesRepresentativeReadModel, country: Country) -> None:
    data = {
        "relation_manager_id": representative_3.id,
        "company_info": {
            "address": {
                "city": "Testowo",
                "country": {"code": country.code, "name": country.name},
                "postal_code": "11-222",
                "street": "Testowa",
                "street_no": "123a",
            },
            "industry": "automotive",
            "legal_form": "limited",
            "name": "Company Ltd.",
            "size": "medium",
        },
    }
    r = client.post("/customers", json=data)
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert result.get("id")


@pytest.mark.usefixtures("change_user_salesman_id")
def test_create_customer_with_invalid_data_should_fail(client: TestClient) -> None:
    data = {
        "relation_manager_id": "invalid id",
        "company_info": {
            "address": {
                "city": "Testowo",
                "country": {"code": "invalid code", "name": "invalid name"},
                "postal_code": "11-222",
                "street": "Testowa",
                "street_no": "123a",
            },
            "industry": "invalid",
            "legal_form": "invalid",
            "name": "Company Ltd.",
            "size": "invalid",
        },
    }
    r = client.post("/customers", json=data)

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("change_user_salesman_id")
def test_update_customer(
    client: TestClient,
    api_customer_without_contact_persons: CustomerReadModel,
    country: Country,
) -> None:
    data = {
        "company_info": {
            "address": {
                "city": "Testowo",
                "country": {"code": country.code, "name": country.name},
                "postal_code": "11-222",
                "street": "Testowa",
                "street_no": "123a",
            },
            "industry": "agriculture",
            "legal_form": "sole proprietorship",
            "name": "New Company Ltd.",
            "size": "micro",
        },
    }
    r = client.put(f"/customers/{api_customer_without_contact_persons.id}", json=data)
    result = r.json()
    fetched_company_info = result.get("company_info")

    assert r.status_code == status.HTTP_200_OK
    assert fetched_company_info.get("industry") == data["company_info"]["industry"]
    assert fetched_company_info.get("legal_form") == data["company_info"]["legal_form"]
    assert fetched_company_info.get("size") == data["company_info"]["size"]
    assert fetched_company_info.get("name") == data["company_info"]["name"]


def test_update_customer_by_non_relation_manager_should_fail(client: TestClient, customer_3: CustomerReadModel) -> None:
    r = client.put(f"/customers/{customer_3.id}", json={"industry": "technology"})

    assert r.status_code == status.HTTP_403_FORBIDDEN


def test_update_customer_with_wrong_id_should_fail(client: TestClient) -> None:
    r = client.put("/customers/invalid", json={})

    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("change_user_salesman_id")
def test_update_customer_with_invalid_data_should_fail(client: TestClient, customer_3: CustomerReadModel) -> None:
    r = client.put(f"/customers/{customer_3.id}", json={"relation_manager_id": "invalid"})

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_customer(client: TestClient, customer_1: CustomerReadModel) -> None:
    r = client.get(f"/customers/{customer_1.id}")
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert result.get("id") == customer_1.id


def test_get_customer_with_invalid_id_should_fail(client: TestClient) -> None:
    r = client.get("/customers/invalid")

    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("change_user_salesman_id")
def test_convert_customer(client: TestClient, api_customer_with_contact_persons: CustomerReadModel) -> None:
    r = client.post(f"/customers/{api_customer_with_contact_persons.id}/convert")

    assert r.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.usefixtures("change_user_salesman_id")
def test_convert_customer_when_customer_does_not_have_contact_persons_should_fail(
    client: TestClient, api_customer_without_contact_persons: CustomerReadModel
) -> None:
    r = client.post(f"/customers/{api_customer_without_contact_persons.id}/convert")

    assert r.status_code == status.HTTP_400_BAD_REQUEST


def test_convert_customer_by_non_relation_manager_should_fail(
    client: TestClient, api_customer_with_contact_persons: CustomerReadModel
) -> None:
    r = client.post(f"/customers/{api_customer_with_contact_persons.id}/convert")

    assert r.status_code == status.HTTP_403_FORBIDDEN


def test_convert_customer_with_wrong_id_should_fail(client: TestClient) -> None:
    r = client.post("/customers/invalid/convert")

    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("change_user_salesman_id")
def test_convert_customer_when_conflicting_with_current_status_should_fail(
    client: TestClient, api_customer_with_contact_persons: CustomerReadModel
) -> None:
    r = client.post(f"/customers/{api_customer_with_contact_persons.id}/convert")

    assert r.status_code == status.HTTP_409_CONFLICT


@pytest.mark.usefixtures("change_user_salesman_id")
def test_archive_customer(client: TestClient, api_customer_with_contact_persons: CustomerReadModel) -> None:
    r = client.post(f"/customers/{api_customer_with_contact_persons.id}/archive")

    assert r.status_code == status.HTTP_204_NO_CONTENT


def test_archive_customer_by_non_relation_manager_should_fail(
    client: TestClient, api_customer_with_contact_persons: CustomerReadModel
) -> None:
    r = client.post(f"/customers/{api_customer_with_contact_persons.id}/archive")

    assert r.status_code == status.HTTP_403_FORBIDDEN


def test_archive_customer_with_wrong_id_should_fail(client: TestClient) -> None:
    r = client.post("/customers/invalid/archive")

    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("change_user_salesman_id")
def test_archive_customer_when_conflicting_with_current_status_should_fail(
    client: TestClient, api_customer_with_contact_persons: CustomerReadModel
) -> None:
    r = client.post(f"/customers/{api_customer_with_contact_persons.id}/archive")

    assert r.status_code == status.HTTP_409_CONFLICT


@pytest.mark.usefixtures("change_user_salesman_id", "api_opportunity")
def test_archive_customer_when_has_open_opportunities_should_fail(
    client: TestClient, api_customer_with_open_opportunity: CustomerReadModel
) -> None:
    r = client.post(f"/customers/{api_customer_with_open_opportunity.id}/archive")

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_customers_contact_persons(
    client: TestClient, customer_1: CustomerReadModel, contact_person: ContactPersonCreateModel
) -> None:
    r = client.get(f"/customers/{customer_1.id}/contact-persons")
    result = r.json()

    fetched_contact_method = result[0].get("contact_methods")[0]
    actual_contact_method = contact_person.contact_methods[0]
    assert r.status_code == status.HTTP_200_OK
    assert result[0].get("first_name") == contact_person.first_name
    assert result[0].get("last_name") == contact_person.last_name
    assert result[0].get("job_title") == contact_person.job_title
    assert fetched_contact_method.get("type") == actual_contact_method.type
    assert fetched_contact_method.get("value") == actual_contact_method.value
    assert fetched_contact_method.get("is_preferred") == actual_contact_method.is_preferred


def test_get_customers_contact_persons_with_wrong_id_should_fail(client: TestClient) -> None:
    r = client.get("/customers/invalid/contact-persons")

    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("change_user_salesman_id")
def test_create_customers_contact_person(
    client: TestClient, api_customer_with_contact_persons: CustomerReadModel, language: Language
) -> None:
    data = {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "job_title": "CEO",
        "preferred_language": {
            "code": language.code,
            "name": language.name,
        },
        "contact_methods": [{"is_preferred": True, "type": "email", "value": "createcontactperson@example.com"}],
    }
    r = client.post(f"/customers/{api_customer_with_contact_persons.id}/contact-persons", json=data)

    assert r.status_code == status.HTTP_200_OK


def test_create_customers_contact_person_by_non_relation_manager_should_fail(
    client: TestClient, api_customer_with_contact_persons: CustomerReadModel, language: Language
) -> None:
    data = {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "job_title": "CEO",
        "preferred_language": {
            "code": language.code,
            "name": language.name,
        },
        "contact_methods": [{"is_preferred": True, "type": "email", "value": "createcontactperson@example.com"}],
    }

    r = client.post(f"/customers/{api_customer_with_contact_persons.id}/contact-persons", json=data)

    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.usefixtures("change_user_salesman_id")
def test_create_customers_contact_person_with_wrong_id_should_fail(client: TestClient, language: Language) -> None:
    data = {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "job_title": "CEO",
        "preferred_language": {
            "code": language.code,
            "name": language.name,
        },
        "contact_methods": [{"is_preferred": True, "type": "email", "value": "createcontactperson@example.com"}],
    }
    r = client.post("/customers/invalid/contact-persons", json=data)

    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("change_user_salesman_id")
def test_create_customers_contact_person_with_invalid_data_should_fail(
    client: TestClient, api_customer_with_contact_persons: CustomerReadModel
) -> None:
    data = {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "job_title": "CEO",
        "contact_methods": [{"is_preferred": True, "type": "invalid", "value": "createcontactperson@example.com"}],
    }

    r = client.post(f"/customers/{api_customer_with_contact_persons.id}/contact-persons", json=data)

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("change_user_salesman_id")
def test_update_customers_contact_person(
    client: TestClient, api_customer_with_contact_persons: CustomerReadModel, api_contact_person: ContactPersonReadModel
) -> None:
    data = {
        "first_name": "Jan",
        "last_name": "Kowalski",
    }

    r = client.put(
        f"/customers/{api_customer_with_contact_persons.id}/contact-persons/{api_contact_person.id}", json=data
    )
    result = r.json()

    assert r.status_code == status.HTTP_200_OK
    assert result.get("first_name") == data["first_name"]
    assert result.get("last_name") == data["last_name"]


def test_update_customers_contact_person_by_non_relation_manager_should_fail(
    client: TestClient, api_customer_with_contact_persons: CustomerReadModel, api_contact_person: ContactPersonReadModel
) -> None:
    data = {
        "first_name": "Jan",
        "last_name": "Kowalski",
    }

    r = client.put(
        f"/customers/{api_customer_with_contact_persons.id}/contact-persons/{api_contact_person.id}", json=data
    )

    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.usefixtures("change_user_salesman_id")
def test_update_customers_contact_person_with_wrong_customer_id_should_fail(
    client: TestClient, api_contact_person: ContactPersonReadModel
) -> None:
    data = {
        "first_name": "Jan",
        "last_name": "Kowalski",
    }

    r = client.put(f"/customers/invalid/contact-persons/{api_contact_person.id}", json=data)

    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("change_user_salesman_id")
def test_update_customers_contact_person_with_wrong_contact_person_id_should_fail(
    client: TestClient, api_customer_with_contact_persons: CustomerReadModel
) -> None:
    data = {
        "first_name": "Jan",
        "last_name": "Kowalski",
    }

    r = client.put(f"/customers/{api_customer_with_contact_persons.id}/contact-persons/invalid", json=data)

    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("change_user_salesman_id")
def test_update_customers_contact_person_with_invalid_data_should_fail(
    client: TestClient, api_customer_with_contact_persons: CustomerReadModel, api_contact_person: ContactPersonReadModel
) -> None:
    data = {"preferred_language": {"name": "invalid", "code": "invalid"}}

    r = client.put(
        f"/customers/{api_customer_with_contact_persons.id}/contact-persons/{api_contact_person.id}", json=data
    )

    assert r.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("change_user_salesman_id")
def test_remove_customers_contact_person(
    client: TestClient, api_customer_with_contact_persons: CustomerReadModel, api_contact_person: ContactPersonReadModel
) -> None:
    r = client.delete(f"/customers/{api_customer_with_contact_persons.id}/contact-persons/{api_contact_person.id}")

    assert r.status_code == status.HTTP_204_NO_CONTENT


def test_remove_customers_contact_person_by_non_relation_manager_should_fail(
    client: TestClient, api_customer_with_contact_persons: CustomerReadModel, api_contact_person: ContactPersonReadModel
) -> None:
    r = client.delete(f"/customers/{api_customer_with_contact_persons.id}/contact-persons/{api_contact_person.id}")

    assert r.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.usefixtures("change_user_salesman_id")
def test_remove_customers_contact_person_with_wrong_customer_id_should_fail(
    client: TestClient, api_contact_person: ContactPersonReadModel
) -> None:
    r = client.delete(f"/customers/invalid/contact-persons/{api_contact_person.id}")

    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures("change_user_salesman_id")
def test_remove_customers_contact_person_with_wrong_contact_person_id_should_fail(
    client: TestClient,
    api_customer_with_contact_persons: CustomerReadModel,
) -> None:
    r = client.delete(f"/customers/{api_customer_with_contact_persons.id}/contact-persons/invalid")

    assert r.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "url,method",
    [
        ("/customers", "get"),
        ("/customers", "post"),
        ("/customers/customer_id", "get"),
        ("/customers/customer_id", "put"),
        ("/customers/customer_id/convert", "post"),
        ("/customers/customer_id/archive", "post"),
        ("/customers/customer_id/contact-persons", "get"),
        ("/customers/customer_id/contact-persons", "post"),
        ("/customers/customer_id/contact-persons/contact_person_id", "put"),
        ("/customers/customer_id/contact-persons/contact_person_id", "delete"),
    ],
)
def test_calling_customer_endpoints_by_guest_should_fail(client: TestClient, url: str, method: str) -> None:
    r = getattr(client, method)(url, headers={"Authorization": ""})

    assert r.status_code == status.HTTP_401_UNAUTHORIZED
