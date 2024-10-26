import pytest
from sqlalchemy.orm import Session

from building_blocks.infrastructure.exceptions import ObjectAlreadyExists
from sales.domain.entities.lead import Lead
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.contact_data import ContactData
from sales.infrastructure.sql.lead.repository import LeadSQLRepository

pytestmark = pytest.mark.integration


@pytest.fixture()
def lead_repo(session: Session) -> LeadSQLRepository:
    return LeadSQLRepository(session)


@pytest.fixture()
def lead() -> Lead:
    contact_data = ContactData(first_name="Jan", last_name="Kowalski", email="email@example.com")
    lead = Lead.make(
        id="some lead",
        customer_id="customer id",
        created_by_salesman_id="salesman id",
        contact_data=contact_data,
        source=AcquisitionSource(name="cold call"),
    )
    return lead


def test_create_and_get(lead_repo: LeadSQLRepository, lead: Lead) -> None:
    lead_repo.create(lead)

    fetched_lead = lead_repo.get(lead.id)

    assert fetched_lead is not None
    assert fetched_lead.id == lead.id


def test_get_by_customer(lead_repo: LeadSQLRepository, lead: Lead) -> None:
    lead_repo.create(lead)

    fetched_lead = lead_repo.get_by_customer(lead.customer_id)

    assert fetched_lead is not None
    assert fetched_lead.id == lead.id


def test_get_by_customer_should_return_none_if_not_found(lead_repo: LeadSQLRepository, lead: Lead) -> None:
    lead_repo.create(lead)

    fetched_lead = lead_repo.get_by_customer("non existent customer")

    assert fetched_lead is None


def test_get_should_return_none_if_not_found(
    lead_repo: LeadSQLRepository,
) -> None:
    fetched_lead = lead_repo.get("invalid id")

    assert fetched_lead is None


def test_create_with_existing_id_should_fail(lead_repo: LeadSQLRepository, lead: Lead) -> None:
    lead_repo.create(lead)

    with pytest.raises(ObjectAlreadyExists):
        lead_repo.create(lead)


def test_update(lead_repo: LeadSQLRepository, lead: Lead) -> None:
    new_source = AcquisitionSource(name="other")
    lead_repo.create(lead)
    lead.update(editor_id=lead.created_by_salesman_id, source=new_source)

    lead_repo.update(lead)

    fetched_lead = lead_repo.get(lead.id)
    assert fetched_lead.source == new_source


def test_update_updates_assignments(
    lead_repo: LeadSQLRepository,
    lead: Lead,
) -> None:
    new_salesman_id = "new salesman id"
    lead_repo.create(lead)
    lead.assign_salesman(new_salesman_id=new_salesman_id, requestor_id=lead.created_by_salesman_id)

    lead_repo.update(lead)
    lead_repo.db.flush()

    fetched_lead = lead_repo.get(lead.id)
    assert fetched_lead.assigned_salesman_id == new_salesman_id


def test_update_updates_notes(lead_repo: LeadSQLRepository, lead: Lead) -> None:
    new_note_content = "this is a note"
    lead_repo.create(lead)
    lead.assign_salesman(new_salesman_id=lead.created_by_salesman_id, requestor_id=lead.created_by_salesman_id)
    lead.change_note(new_content=new_note_content, editor_id=lead.created_by_salesman_id)

    lead_repo.update(lead)
    lead_repo.db.flush()

    fetched_lead = lead_repo.get(lead.id)
    assert fetched_lead.note.content == new_note_content
