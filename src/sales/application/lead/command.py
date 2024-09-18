from uuid import uuid4

from building_blocks.domain.exceptions import (
    InvalidEmailAddress,
    InvalidPhoneNumber,
    ValueNotAllowed,
)
from sales.application.lead.command_model import (
    AssignmentUpdateModel,
    ContactDataCreateUpdateModel,
    LeadCreateModel,
    LeadUpdateModel,
)
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.domain.entities.lead import Lead
from sales.domain.repositories.lead import LeadRepository
from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.contact_data import ContactData
from sales.domain.exceptions import (
    EmailOrPhoneNumberShouldBeSet,
    OnlyOwnerCanEditNotes,
    UnauthorizedLeadOwnerChange,
)
from sales.application.notes.command_model import NoteCreateModel
from sales.application.notes.query_model import NoteReadModel
from building_blocks.application.command import BaseUnitOfWork
from building_blocks.application.exceptions import (
    InvalidData,
    ObjectDoesNotExist,
    UnauthorizedAction,
)


class LeadUnitOfWork(BaseUnitOfWork):
    repository: LeadRepository


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
            uow.repository.create(lead)
        return LeadReadModel.from_domain(lead)

    def update(self, lead_id: str, lead_data: LeadUpdateModel) -> LeadReadModel:
        with self.lead_uow as uow:
            lead = self._get_lead(uow=uow, lead_id=lead_id)
            if lead_data.source is not None:
                lead.source = self._create_source(lead_data.source)
            if lead_data.contact_data is not None:
                lead.contact_data = self._create_contact_data(lead_data.contact_data)
            uow.repository.update(lead)
        return LeadReadModel.from_domain(lead)

    def update_note(
        self, lead_id: str, editor_id: str, note_data: NoteCreateModel
    ) -> NoteReadModel:
        with self.lead_uow as uow:
            lead = self._get_lead(uow=uow, lead_id=lead_id)
            try:
                lead.change_note(new_content=note_data.content, editor_id=editor_id)
            except OnlyOwnerCanEditNotes as e:
                raise UnauthorizedAction(e.message)
            uow.repository.update(lead)
        return NoteReadModel.from_domain(lead.note)

    def update_assignment(
        self, lead_id: str, requestor_id: str, assignment_data: AssignmentUpdateModel
    ) -> AssignmentReadModel:
        with self.lead_uow as uow:
            lead = self._get_lead(uow=uow, lead_id=lead_id)
            try:
                lead.assign_salesman(
                    new_salesman_id=assignment_data.new_salesman_id,
                    requestor_id=requestor_id,
                )
            except UnauthorizedLeadOwnerChange as e:
                raise UnauthorizedAction(e.message)
            uow.repository.update(lead)
        return AssignmentReadModel.from_domain(lead.most_recent_assignment)

    def _get_lead(self, uow: LeadUnitOfWork, lead_id: str) -> Lead:
        lead = uow.repository.get(lead_id)
        if lead is None:
            raise ObjectDoesNotExist(lead_id)
        return lead

    def _create_source(self, source_name: str) -> AcquisitionSource:
        try:
            source = AcquisitionSource(name=source_name)
        except ValueNotAllowed as e:
            raise InvalidData(e.message)
        return source

    def _create_contact_data(self, data: ContactDataCreateUpdateModel) -> ContactData:
        try:
            contact_data = ContactData(
                first_name=data.first_name,
                last_name=data.last_name,
                company_name=data.company_name,
                phone=data.phone,
                email=data.email,
            )
        except (
            InvalidPhoneNumber,
            InvalidEmailAddress,
            EmailOrPhoneNumberShouldBeSet,
        ) as e:
            raise InvalidData(e.message)
        return contact_data
