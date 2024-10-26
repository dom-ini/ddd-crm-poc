import datetime as dt
from unittest.mock import MagicMock

import pytest

from building_blocks.domain.exceptions import InvalidEmailAddress, InvalidPhoneNumber, ValueNotAllowed
from sales.domain.entities.lead import Lead
from sales.domain.entities.lead_assignments import LeadAssignments
from sales.domain.entities.notes import Notes
from sales.domain.exceptions import (
    CanCreateOnlyOneLeadPerCustomer,
    LeadAlreadyAssignedToSalesman,
    LeadCanBeCreatedOnlyForInitialCustomer,
    OnlyOwnerCanEditNotes,
    OnlyOwnerCanModifyLeadData,
    UnauthorizedLeadOwnerChange,
)
from sales.domain.service.lead import ensure_customer_has_initial_status, ensure_one_lead_per_customer
from sales.domain.service.shared import SalesCustomerStatusName
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.contact_data import ContactData
from sales.domain.value_objects.lead_assignment_entry import LeadAssignmentEntry
from sales.domain.value_objects.note import Note


@pytest.fixture()
def lead_repo() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def contact_data() -> ContactData:
    return ContactData(
        first_name="Jan",
        last_name="Kowalski",
        phone="+48123123123",
        email="test@example.com",
    )


@pytest.fixture()
def contact_data_2() -> ContactData:
    return ContactData(
        first_name="Piotr",
        last_name="Nowak",
        phone="+48321321321",
        email="test2@example.com",
    )


@pytest.fixture()
def lead(contact_data: ContactData, source: AcquisitionSource) -> Lead:
    return Lead.make(
        id="lead_1",
        customer_id="customer_1",
        created_by_salesman_id="salesman_1",
        contact_data=contact_data,
        source=source,
    )


@pytest.fixture()
def assignment() -> LeadAssignmentEntry:
    return LeadAssignmentEntry(
        previous_owner_id=None,
        new_owner_id="salesman_1",
        assigned_by_id="salesman_1",
        assigned_at=dt.datetime.now(),
    )


def test_creation_contact_data_with_invalid_email_should_fail(
    contact_data: ContactData,
) -> None:
    with pytest.raises(InvalidEmailAddress):
        ContactData(
            first_name=contact_data.first_name,
            last_name=contact_data.last_name,
            phone=contact_data.phone,
            email="invalid email",
        )


def test_creation_contact_data_with_invalid_phone_should_fail(
    contact_data: ContactData,
) -> None:
    with pytest.raises(InvalidPhoneNumber):
        ContactData(
            first_name=contact_data.first_name,
            last_name=contact_data.last_name,
            phone="invalid phone",
            email=contact_data.email,
        )


def test_acqusition_source_with_invalid_name_should_fail() -> None:
    with pytest.raises(ValueNotAllowed):
        AcquisitionSource(name="invalid")


def test_lead_creation(lead: Lead, contact_data: ContactData, source: AcquisitionSource):
    assert lead.id == "lead_1"
    assert lead.customer_id == "customer_1"
    assert lead.contact_data == contact_data
    assert lead.source == source
    assert lead.created_by_salesman_id == "salesman_1"
    assert isinstance(lead.created_at, dt.datetime)
    assert lead.assigned_salesman_id is None
    assert lead.note is None
    assert len(lead.notes_history) == 0


def test_lead_reconstitution(
    contact_data: ContactData,
    source: AcquisitionSource,
    note: Note,
    assignment: LeadAssignmentEntry,
) -> None:
    assignments = LeadAssignments(history=(assignment,))
    notes = Notes(history=(note,))
    created_at = dt.datetime(2023, 1, 1)

    lead = Lead.reconstitute(
        id="lead_1",
        customer_id="customer_1",
        created_by_salesman_id="salesman_1",
        created_at=created_at,
        contact_data=contact_data,
        source=source,
        assignments=assignments,
        notes=notes,
    )

    assert lead.id == "lead_1"
    assert lead.customer_id == "customer_1"
    assert lead.created_at == created_at
    assert lead.contact_data == contact_data
    assert lead.source == source
    assert lead.assigned_salesman_id == assignment.new_owner_id
    assert lead.note == note


def test_new_lead_update(lead: Lead, contact_data_2: ContactData, source_2: AcquisitionSource) -> None:
    lead.update(
        editor_id=lead.created_by_salesman_id,
        contact_data=contact_data_2,
        source=source_2,
    )

    assert lead.source == source_2
    assert lead.contact_data == contact_data_2


def test_assigned_lead_update(lead: Lead, contact_data_2: ContactData, source_2: AcquisitionSource) -> None:
    owner_id = "salesman_2"
    lead.assign_salesman(new_salesman_id=owner_id, requestor_id=owner_id)

    lead.update(
        editor_id=lead.assigned_salesman_id,
        source=source_2,
        contact_data=contact_data_2,
    )

    assert lead.source == source_2
    assert lead.contact_data == contact_data_2


def test_lead_partial_update(lead: Lead, source_2: AcquisitionSource) -> None:
    old_contact_data = lead.contact_data
    lead.update(editor_id=lead.created_by_salesman_id, source=source_2)

    assert lead.source == source_2
    assert lead.contact_data == old_contact_data


def test_new_lead_update_by_non_creator_should_fail(
    lead: Lead, contact_data_2: ContactData, source_2: AcquisitionSource
) -> None:
    with pytest.raises(OnlyOwnerCanModifyLeadData):
        lead.update(editor_id="non creator id", source=source_2, contact_data=contact_data_2)


def test_assigned_lead_update_by_non_owner_should_fail(
    lead: Lead, contact_data_2: ContactData, source_2: AcquisitionSource
) -> None:
    owner_id = "salesman_2"
    lead.assign_salesman(new_salesman_id=owner_id, requestor_id=owner_id)

    with pytest.raises(OnlyOwnerCanModifyLeadData):
        lead.update(
            editor_id=lead.created_by_salesman_id,
            source=source_2,
            contact_data=contact_data_2,
        )


def test_assign_salesman_to_new_lead(lead: Lead) -> None:
    lead.assign_salesman(new_salesman_id="salesman_2", requestor_id="salesman_1")
    assert lead.assigned_salesman_id == "salesman_2"


def test_assign_salesman_by_current_owner(lead: Lead) -> None:
    lead.assign_salesman(new_salesman_id="salesman_2", requestor_id="salesman_1")
    lead.assign_salesman(new_salesman_id="salesman_3", requestor_id="salesman_2")
    assert lead.assigned_salesman_id == "salesman_3"


def test_assign_salesman_by_non_owner_should_fail(lead: Lead) -> None:
    lead.assign_salesman(new_salesman_id="salesman_2", requestor_id="salesman_1")
    with pytest.raises(UnauthorizedLeadOwnerChange):
        lead.assign_salesman(new_salesman_id="salesman_3", requestor_id="salesman_4")


def test_change_note_by_assigned_salesman(lead: Lead) -> None:
    lead.assign_salesman(new_salesman_id="salesman_1", requestor_id="salesman_1")
    lead.change_note(new_content="Updated Note", editor_id="salesman_1")
    assert lead.note.content == "Updated Note"


def test_change_note_by_non_owner_should_fail(lead: Lead) -> None:
    lead.assign_salesman(new_salesman_id="salesman_1", requestor_id="salesman_1")
    with pytest.raises(OnlyOwnerCanEditNotes):
        lead.change_note(new_content="Unauthorized Note Change", editor_id="salesman_2")


def test_change_note_on_unassigned_lead_should_fail(lead: Lead) -> None:
    with pytest.raises(OnlyOwnerCanEditNotes):
        lead.change_note(new_content="Unauthorized Note Change", editor_id="salesman_1")


def test_notes_history_is_properly_saved(lead: Lead) -> None:
    lead.assign_salesman(new_salesman_id="salesman_1", requestor_id="salesman_1")
    lead.change_note(new_content="First Note", editor_id=lead.assigned_salesman_id)
    lead.change_note(new_content="Second Note", editor_id=lead.assigned_salesman_id)

    assert len(lead.notes_history) == 2
    assert lead.notes_history[0].content == "First Note"
    assert lead.notes_history[1].content == "Second Note"


def test_assignment_history_is_properly_saved(lead: Lead) -> None:
    lead.assign_salesman(new_salesman_id="salesman_1", requestor_id="salesman_1")
    lead.assign_salesman(new_salesman_id="salesman_2", requestor_id="salesman_1")

    assert len(lead.assignment_history) == 2
    assert lead.assignment_history[0].new_owner_id == "salesman_1"
    assert lead.assignment_history[1].new_owner_id == "salesman_2"


def test_assigning_lead_to_current_owner_should_fail(lead: Lead) -> None:
    lead.assign_salesman(new_salesman_id=lead.created_by_salesman_id, requestor_id=lead.created_by_salesman_id)

    with pytest.raises(LeadAlreadyAssignedToSalesman):
        lead.assign_salesman(new_salesman_id=lead.assigned_salesman_id, requestor_id=lead.assigned_salesman_id)


def test_ensure_one_lead_per_customer_should_not_fail_when_lead_does_not_exist(lead_repo: MagicMock) -> None:
    lead_repo.get_by_customer.return_value = None

    ensure_one_lead_per_customer(lead_repo=lead_repo, customer_id="customer id")


def test_ensure_one_lead_per_customer_should_fail_if_lead_already_exists(lead_repo: MagicMock) -> None:
    lead_repo.get_by_customer.return_value = MagicMock()

    with pytest.raises(CanCreateOnlyOneLeadPerCustomer):
        ensure_one_lead_per_customer(lead_repo=lead_repo, customer_id="customer id")


def test_ensure_customer_has_initial_status_should_not_fail_if_customer_has_initial_status() -> None:
    ensure_customer_has_initial_status(SalesCustomerStatusName.INITIAL)


@pytest.mark.parametrize("status", [SalesCustomerStatusName.CONVERTED, SalesCustomerStatusName.ARCHIVED])
def test_ensure_customer_has_initial_status_should_fail_if_customer_has_other_status(status: str) -> None:
    with pytest.raises(LeadCanBeCreatedOnlyForInitialCustomer):
        ensure_customer_has_initial_status(status)
