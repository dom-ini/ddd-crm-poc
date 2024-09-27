from collections.abc import Iterator, Sequence
from uuid import uuid4

import pytest

from building_blocks.application.filters import FilterCondition, FilterConditionType
from sales.application.lead.command import LeadCommandUseCase
from sales.application.lead.command_model import AssignmentUpdateModel, ContactDataCreateUpdateModel, LeadCreateModel
from sales.application.lead.query_model import LeadReadModel
from sales.application.notes.command_model import NoteCreateModel
from sales.infrastructure.file.lead.command import LeadFileUnitOfWork
from sales.infrastructure.file.lead.query_service import LeadFileQueryService
from tests.infrastructure.file.conftest import TEST_DATA_FOLDER

pytestmark = pytest.mark.integration

LEADS_QUERY_DB_FILE = "test-query-leads"
TEST_DATA_PATH = TEST_DATA_FOLDER / LEADS_QUERY_DB_FILE


@pytest.fixture(scope="session")
def command_use_case() -> LeadCommandUseCase:
    uow = LeadFileUnitOfWork(file_path=TEST_DATA_PATH)
    command_use_case = LeadCommandUseCase(lead_uow=uow)
    return command_use_case


@pytest.fixture(scope="session")
def salesman_1_id() -> str:
    return str(uuid4())


@pytest.fixture(scope="session")
def salesman_2_id() -> str:
    return str(uuid4())


@pytest.fixture(scope="session")
def note_content() -> str:
    return "This is a note"


@pytest.fixture(scope="session")
def new_salesman_id() -> str:
    return str(uuid4())


@pytest.fixture(scope="session", autouse=True)
def lead_1(
    command_use_case: LeadCommandUseCase,
    salesman_1_id: str,
    note_content: str,
    new_salesman_id: str,
) -> LeadReadModel:
    contact_data = ContactDataCreateUpdateModel(
        first_name="Jan",
        last_name="Kowalski",
        phone="+48123456789",
        email="jan.kowalski@example.com",
    )
    lead_data = LeadCreateModel(customer_id=str(uuid4()), source="ads", contact_data=contact_data)
    lead = command_use_case.create(lead_data=lead_data, creator_id=salesman_1_id)

    command_use_case.update_assignment(
        lead_id=lead.id,
        requestor_id=lead.created_by_salesman_id,
        assignment_data=AssignmentUpdateModel(new_salesman_id=new_salesman_id),
    )
    command_use_case.update_note(
        lead_id=lead.id,
        editor_id=new_salesman_id,
        note_data=NoteCreateModel(content=note_content),
    )

    return lead


@pytest.fixture(scope="session", autouse=True)
def lead_2(command_use_case: LeadCommandUseCase, salesman_1_id: str) -> LeadReadModel:
    contact_data = ContactDataCreateUpdateModel(
        first_name="Jan",
        last_name="Nowak",
        phone="+48123123456",
        email="piotr.nowak@example.com",
    )
    lead_data = LeadCreateModel(customer_id=str(uuid4()), source="cold call", contact_data=contact_data)
    return command_use_case.create(lead_data=lead_data, creator_id=salesman_1_id)


@pytest.fixture(scope="session", autouse=True)
def lead_3(command_use_case: LeadCommandUseCase, salesman_2_id: str) -> LeadReadModel:
    contact_data = ContactDataCreateUpdateModel(
        first_name="Paweł", last_name="Kowalczyk", email="pawel.kowalczyk@example.com"
    )
    lead_data = LeadCreateModel(customer_id=str(uuid4()), source="website", contact_data=contact_data)
    return command_use_case.create(lead_data=lead_data, creator_id=salesman_2_id)


@pytest.fixture()
def all_leads(lead_1: LeadReadModel, lead_2: LeadReadModel, lead_3: LeadReadModel) -> Sequence[LeadReadModel]:
    return (lead_1, lead_2, lead_3)


@pytest.fixture(scope="session", autouse=True)
def clean_data() -> Iterator[None]:
    yield
    for file in TEST_DATA_FOLDER.iterdir():
        if file.name.startswith(LEADS_QUERY_DB_FILE):
            file.unlink()


@pytest.fixture()
def query_service() -> LeadFileQueryService:
    return LeadFileQueryService(leads_file_path=TEST_DATA_PATH)


def test_get_lead(query_service: LeadFileQueryService, lead_1: LeadReadModel) -> None:
    lead = query_service.get(lead_id=lead_1.id)

    assert lead is not None
    assert lead.id == lead_1.id


def test_get_all(query_service: LeadFileQueryService, all_leads: Sequence[LeadReadModel]) -> None:
    leads = query_service.get_all()

    fetched_leads_ids = set(lead.id for lead in leads)
    leads_ids = set(lead.id for lead in all_leads)
    assert fetched_leads_ids == leads_ids


def test_get_filtered(query_service: LeadFileQueryService, lead_1: LeadReadModel, lead_2: LeadReadModel) -> None:
    filters = [
        FilterCondition(
            field="contact_data.first_name",
            value="Jan",
            condition_type=FilterConditionType.EQUALS,
        )
    ]
    leads = query_service.get_filtered(filters)

    fetched_leads_ids = set(lead.id for lead in leads)
    assert fetched_leads_ids == {lead_1.id, lead_2.id}


def test_get_assignment_history(
    query_service: LeadFileQueryService, lead_1: LeadReadModel, new_salesman_id: str
) -> None:
    assignments = query_service.get_assignment_history(lead_id=lead_1.id)

    assert assignments is not None
    assert assignments[0].new_owner_id == new_salesman_id


def test_get_notes(query_service: LeadFileQueryService, lead_1: LeadReadModel, note_content: str) -> None:
    notes = query_service.get_notes(lead_id=lead_1.id)

    assert notes is not None
    assert notes[0].content == note_content


@pytest.mark.parametrize("method_name", ["get", "get_assignment_history", "get_notes"])
def test_methods_should_return_none_if_not_found(query_service: LeadFileQueryService, method_name: str) -> None:
    lead = getattr(query_service, method_name)(lead_id="invalid id")

    assert lead is None
