from unittest.mock import MagicMock

import pytest

from building_blocks.application.exceptions import InvalidData, ObjectDoesNotExist, UnauthorizedAction
from building_blocks.domain.exceptions import DomainException, InvalidEmailAddress, InvalidPhoneNumber, ValueNotAllowed
from sales.application.lead.command import LeadCommandUseCase, LeadUnitOfWork
from sales.application.lead.command_model import ContactDataCreateUpdateModel, LeadCreateModel, LeadUpdateModel
from sales.domain.entities.lead import Lead
from sales.domain.exceptions import (
    EmailOrPhoneNumberShouldBeSet,
    OnlyOwnerCanEditNotes,
    OnlyOwnerCanModifyLeadData,
    UnauthorizedLeadOwnerChange,
)
from sales.domain.repositories.lead import LeadRepository


@pytest.fixture()
def mock_lead_repository() -> LeadRepository:
    repository = MagicMock(spec=LeadRepository)
    return repository


@pytest.fixture()
def lead_uow(mock_lead_repository: LeadRepository) -> LeadUnitOfWork:
    uow = MagicMock(spec=LeadUnitOfWork)
    uow.repository = mock_lead_repository
    return uow


@pytest.fixture()
def lead_command_use_case(lead_uow: LeadUnitOfWork) -> LeadCommandUseCase:
    return LeadCommandUseCase(lead_uow=lead_uow)


@pytest.fixture()
def mock_lead() -> MagicMock:
    return MagicMock(spec=Lead)


@pytest.mark.parametrize(
    "data",
    [
        LeadCreateModel(
            customer_id="customer-1",
            source="website",
            contact_data=ContactDataCreateUpdateModel(
                first_name="John",
                last_name="Doe",
                phone=None,
                email="invalid email",
            ),
        ),
        LeadCreateModel(
            customer_id="customer-1",
            source="website",
            contact_data=ContactDataCreateUpdateModel(
                first_name="John",
                last_name="Doe",
                phone="invalid phone",
                email=None,
            ),
        ),
        LeadCreateModel(
            customer_id="customer-1",
            source="website",
            contact_data=ContactDataCreateUpdateModel(first_name="John", last_name="Doe", phone=None, email=None),
        ),
        LeadCreateModel(
            customer_id="customer-1",
            source="invalid source",
            contact_data=ContactDataCreateUpdateModel(
                first_name="John",
                last_name="Doe",
                phone="+48123123123",
                email="test@example.com",
            ),
        ),
    ],
)
def test_create_lead_correctly_raises_invalid_data(
    lead_uow: LeadUnitOfWork,
    lead_command_use_case: LeadCommandUseCase,
    data: LeadCreateModel,
) -> None:
    with pytest.raises(InvalidData):
        lead_command_use_case.create(lead_data=data, creator_id="salesman-1")

    lead_uow.__enter__().repository.create.assert_not_called()


@pytest.mark.parametrize(
    "data,causing_exc_class",
    [
        (
            LeadUpdateModel(
                source="website",
                contact_data=ContactDataCreateUpdateModel(
                    first_name="John",
                    last_name="Doe",
                    phone=None,
                    email="invalid email",
                ),
            ),
            InvalidEmailAddress,
        ),
        (
            LeadUpdateModel(
                source="website",
                contact_data=ContactDataCreateUpdateModel(
                    first_name="John",
                    last_name="Doe",
                    phone="invalid phone",
                    email=None,
                ),
            ),
            InvalidPhoneNumber,
        ),
        (
            LeadUpdateModel(
                source="website",
                contact_data=ContactDataCreateUpdateModel(first_name="John", last_name="Doe", phone=None, email=None),
            ),
            EmailOrPhoneNumberShouldBeSet,
        ),
        (
            LeadUpdateModel(
                source="invalid source",
                contact_data=ContactDataCreateUpdateModel(
                    first_name="John",
                    last_name="Doe",
                    phone="+48123123123",
                    email="test@example.com",
                ),
            ),
            ValueNotAllowed,
        ),
    ],
)
def test_update_lead_correctly_raises_invalid_data(
    lead_uow: LeadUnitOfWork,
    lead_command_use_case: LeadCommandUseCase,
    data: LeadUpdateModel,
    causing_exc_class: type[DomainException],
) -> None:
    with pytest.raises(InvalidData) as exc_info:
        lead_command_use_case.update(lead_id="lead-1", lead_data=data, editor_id="salesman-1")

    assert isinstance(exc_info.value.__cause__, causing_exc_class)
    lead_uow.__enter__().repository.update.assert_not_called()


@pytest.mark.parametrize(
    "method_name,data_field_name,editor_field_name",
    [
        ("update", "lead_data", "editor_id"),
        ("update_note", "note_data", "editor_id"),
        ("update_assignment", "assignment_data", "requestor_id"),
    ],
)
def test_calling_method_with_wrong_lead_id_should_fail(
    lead_uow: LeadUnitOfWork,
    lead_command_use_case: LeadCommandUseCase,
    method_name: str,
    data_field_name: str,
    editor_field_name: str,
) -> None:
    lead_id = "invalid id"
    data = MagicMock()
    lead_uow.__enter__().repository.get.return_value = None
    kwargs = {"lead_id": lead_id, data_field_name: data, editor_field_name: "salesman-1"}

    with pytest.raises(ObjectDoesNotExist):
        getattr(lead_command_use_case, method_name)(**kwargs)

    lead_uow.__enter__().repository.update.assert_not_called()


def test_update_by_unauthorized_user_should_fail(
    lead_uow: LeadUnitOfWork,
    lead_command_use_case: LeadCommandUseCase,
    mock_lead: MagicMock,
) -> None:
    lead_uow.__enter__().repository.get.return_value = mock_lead
    mock_lead.update.side_effect = OnlyOwnerCanModifyLeadData
    data = LeadUpdateModel(
        source="website",
        contact_data=ContactDataCreateUpdateModel(
            first_name="John",
            last_name="Doe",
            phone=None,
            email="email@example.com",
        ),
    )

    with pytest.raises(UnauthorizedAction):
        lead_command_use_case.update(lead_id="lead-1", editor_id="salesman-1", lead_data=data)


def test_update_note_by_unauthorized_user_should_fail(
    lead_uow: LeadUnitOfWork,
    lead_command_use_case: LeadCommandUseCase,
    mock_lead: MagicMock,
) -> None:
    lead_uow.__enter__().repository.get.return_value = mock_lead
    mock_lead.change_note.side_effect = OnlyOwnerCanEditNotes

    with pytest.raises(UnauthorizedAction):
        lead_command_use_case.update_note(lead_id="lead-1", editor_id="salesman-1", note_data=MagicMock())


def test_update_assignment_by_unauthorized_user_should_fail(
    lead_uow: LeadUnitOfWork,
    lead_command_use_case: LeadCommandUseCase,
    mock_lead: MagicMock,
) -> None:
    lead_uow.__enter__().repository.get.return_value = mock_lead
    mock_lead.assign_salesman.side_effect = UnauthorizedLeadOwnerChange

    with pytest.raises(UnauthorizedAction):
        lead_command_use_case.update_assignment(
            lead_id="lead-1", requestor_id="salesman-1", assignment_data=MagicMock()
        )