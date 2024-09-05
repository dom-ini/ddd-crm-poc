from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.lead.query_service import LeadQueryService
from sales.application.notes.query_model import NoteReadModel


class LeadQueryUseCase:
    def __init__(self, lead_query_service: LeadQueryService) -> None:
        self.lead_query_service = lead_query_service

    def get(self, lead_id: str) -> LeadReadModel:
        return self.lead_query_service.get(lead_id=lead_id)

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
        return assignments

    def get_notes(self, lead_id: str) -> tuple[NoteReadModel, ...]:
        notes = self.lead_query_service.get_notes(lead_id)
        return notes
