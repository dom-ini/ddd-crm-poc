from sales.application.lead.exceptions import LeadDoesNotExist
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.lead.query_service import LeadQueryService
from sales.application.notes.query_model import NoteReadModel


class LeadQueryUseCase:
    def __init__(self, lead_query_service: LeadQueryService) -> None:
        self.lead_query_service = lead_query_service

    def get(self, lead_id: str) -> LeadReadModel:
        lead = self.lead_query_service.get(lead_id)
        if lead is None:
            raise LeadDoesNotExist
        return lead

    def get_all(self) -> tuple[LeadReadModel]:
        leads = self.lead_query_service.get_all()
        return leads

    def get_by_customer_and_owner(
        self, owner_id: str | None = None, customer_id: str | None = None
    ) -> tuple[LeadReadModel]:
        leads = self.lead_query_service.get_by_customer_and_owner_id(
            owner_id=owner_id, customer_id=customer_id
        )
        return leads

    def get_assignment_history(self, lead_id: str) -> tuple[AssignmentReadModel, ...]:
        assignments = self.lead_query_service.get_assignment_history(lead_id)
        if assignments is None:
            raise LeadDoesNotExist
        return assignments

    def get_notes(self, lead_id: str) -> tuple[NoteReadModel, ...]:
        notes = self.lead_query_service.get_notes(lead_id)
        if notes is None:
            raise LeadDoesNotExist
        return notes
