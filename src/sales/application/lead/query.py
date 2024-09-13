from sales.application.lead.exceptions import LeadDoesNotExist
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.lead.query_service import LeadQueryService
from sales.application.notes.query_model import NoteReadModel
from src.building_blocks.application.filters import FilterCondition, FilterConditionType


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

    def get_filtered(
        self,
        customer_id: str | None = None,
        owner_id: str | None = None,
        contact_company_name: str | None = None,
        contact_phone: str | None = None,
        contact_email: str | None = None,
    ) -> tuple[LeadReadModel]:
        filters = [
            FilterCondition(
                field="customer_id",
                value=customer_id,
                condition_type=FilterConditionType.EQUALS,
            ),
            FilterCondition(
                field="salesman_id",
                value=owner_id,
                condition_type=FilterConditionType.EQUALS,
            ),
            FilterCondition(
                field="contact_data.phone",
                value=contact_phone,
                condition_type=FilterConditionType.ICONTAINS,
            ),
            FilterCondition(
                field="contact_data.email",
                value=contact_email,
                condition_type=FilterConditionType.ICONTAINS,
            ),
            FilterCondition(
                field="contact_data.company_name",
                value=contact_company_name,
                condition_type=FilterConditionType.ICONTAINS,
            ),
        ]
        leads = self.lead_query_service.get_filtered(filters)
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
