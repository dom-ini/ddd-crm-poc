from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self
from uuid import uuid4

from building_blocks.domain.exceptions import (
    InvalidEmailAddress,
    InvalidPhoneNumber,
    ValueNotAllowed,
)
from sales.application.lead.command_model import (
    AssignmentUpdateModel,
    LeadCreateModel,
    LeadUpdateModel,
)
from sales.application.lead.exceptions import InvalidLeadData
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.domain.entities.lead import Lead
from sales.domain.repositories.lead import LeadRepository
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.contact_data import ContactData
from sales.domain.exceptions import EmailOrPhoneNumberShouldBeSet
from sales.application.notes.command_model import NoteCreateModel
from sales.application.notes.query_model import NoteReadModel


class LeadUnitOfWork(ABC):
    lead_repository: LeadRepository

    @abstractmethod
    def begin(self) -> None: ...

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...

    def __enter__(self) -> Self:
        self.begin()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
            raise exc_value


class LeadCommandUseCase:
    def __init__(self, lead_uow: LeadUnitOfWork) -> None:
        self.lead_uow = lead_uow

    def create(self, lead_data: LeadCreateModel, creator_id: str) -> LeadReadModel:
        # sprawdzać czy klient istnieje
        lead_id = str(uuid4())
        source, contact_data = self._create_contact_data_and_source(lead_data)
        lead = Lead.make(
            id=lead_id,
            customer_id=lead_data.customer_id,
            created_by_salesman_id=creator_id,
            contact_data=contact_data,
            source=source,
        )
        with self.lead_uow as uow:
            uow.lead_repository.create(lead)
        return LeadReadModel.from_domain(lead)

    def update(self, lead_id: str, lead_data: LeadUpdateModel) -> LeadReadModel:
        with self.lead_uow as uow:
            lead = uow.lead_repository.get(lead_id)
            source, contact_data = self._create_contact_data_and_source(lead_data)
            lead.source = source
            lead.contact_data = contact_data
            uow.lead_repository.update(lead)

        return LeadReadModel.from_domain(lead)

    def update_note(
        self, lead_id: str, editor_id: str, note_data: NoteCreateModel
    ) -> NoteReadModel:
        with self.lead_uow as uow:
            lead = uow.lead_repository.get(lead_id)
            lead.change_note(new_content=note_data.content, editor_id=editor_id)
            uow.lead_repository.update(lead)
        return NoteReadModel.from_domain(lead.note)

    def update_assignment(
        self, lead_id: str, requestor_id: str, assignment_data: AssignmentUpdateModel
    ) -> AssignmentReadModel:
        with self.lead_uow as uow:
            lead = uow.lead_repository.get(lead_id)
            lead.assign_salesman(
                new_salesman_id=assignment_data.new_salesman_id,
                requestor_id=requestor_id,
            )
            uow.lead_repository.update(lead)
        return AssignmentReadModel.from_domain(lead.most_recent_assignment)

    def _create_contact_data_and_source(
        self, lead_data: LeadCreateModel | LeadUpdateModel
    ) -> tuple[AcquisitionSource, ContactData]:
        try:
            source = AcquisitionSource(name=lead_data.source)
            contact_data = ContactData(
                first_name=lead_data.contact_first_name,
                last_name=lead_data.contact_last_name,
                company_name=lead_data.contact_company_name,
                phone=lead_data.contact_phone,
                email=lead_data.contact_email,
            )
        except (
            InvalidPhoneNumber,
            InvalidEmailAddress,
            EmailOrPhoneNumberShouldBeSet,
            ValueNotAllowed,
        ) as e:
            raise InvalidLeadData(e.message)
        return source, contact_data
