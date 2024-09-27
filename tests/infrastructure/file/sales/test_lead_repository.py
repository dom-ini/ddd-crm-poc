from uuid import uuid4

import pytest
from attrs import define

from building_blocks.infrastructure.exceptions import ObjectAlreadyExists
from sales.infrastructure.file.lead.repository import LeadFileRepository

pytestmark = pytest.mark.integration


@define
class DummyLead:
    id: str
    assigned_salesman_id: str


@pytest.fixture(scope="session")
def lead() -> DummyLead:
    return DummyLead(id=str(uuid4()), assigned_salesman_id="some id")


@pytest.fixture(scope="session")
def lead_repo() -> LeadFileRepository:
    return LeadFileRepository(db={})


@pytest.fixture()
def create_lead(lead_repo: LeadFileRepository, lead: DummyLead) -> None:
    lead_repo.create(lead)


@pytest.mark.usefixtures("create_lead")
def test_create_and_get(lead_repo: LeadFileRepository, lead: DummyLead) -> None:
    fetched_lead = lead_repo.get(lead.id)

    assert fetched_lead is not None
    assert fetched_lead.id == lead.id


def test_get_should_return_none_if_not_found(lead_repo: LeadFileRepository) -> None:
    fetched_lead = lead_repo.get("invalid id")

    assert fetched_lead is None


def test_create_with_existing_id_should_fail(lead_repo: LeadFileRepository, lead: DummyLead) -> None:
    with pytest.raises(ObjectAlreadyExists):
        lead_repo.create(lead)


def test_update(lead_repo: LeadFileRepository, lead: DummyLead) -> None:
    new_salesman_id = "new id"
    updated_lead = DummyLead(id=lead.id, assigned_salesman_id=new_salesman_id)

    lead_repo.update(updated_lead)

    fetched_lead = lead_repo.get(lead.id)
    assert fetched_lead.assigned_salesman_id == new_salesman_id
