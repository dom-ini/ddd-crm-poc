from collections.abc import Iterable

from building_blocks.application.exceptions import ObjectDoesNotExist
from building_blocks.application.filters import FilterCondition, FilterConditionType
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.lead.query_service import LeadQueryService
from sales.application.notes.query_model import NoteReadModel


class LeadQueryUseCase:
    def __init__(self, lead_query_service: LeadQueryService) -> None:
        self.lead_query_service = lead_query_service

    def get(self, lead_id: str) -> LeadReadModel:
        lead = self.lead_query_service.get(lead_id)
        if lead is None:
            raise ObjectDoesNotExist(lead_id)
        return lead

    def get_all(self) -> Iterable[LeadReadModel]:
        leads = self.lead_query_service.get_all()
        return leads

    def get_filtered(
        self,
        customer_id: str | None = None,
        owner_id: str | None = None,
        contact_phone: str | None = None,
        contact_email: str | None = None,
    ) -> Iterable[LeadReadModel]:
        filters = [
            FilterCondition(
                field="customer_id",
                value=customer_id,
                condition_type=FilterConditionType.EQUALS,
            ),
            FilterCondition(
                field="assigned_salesman_id",
                value=owner_id,
                condition_type=FilterConditionType.EQUALS,
            ),
            FilterCondition(
                field="contact_data.phone",
                value=contact_phone,
                condition_type=FilterConditionType.SEARCH,
            ),
            FilterCondition(
                field="contact_data.email",
                value=contact_email,
                condition_type=FilterConditionType.SEARCH,
            ),
        ]
        leads = self.lead_query_service.get_filtered(filters)
        return leads

    def get_assignment_history(self, lead_id: str) -> Iterable[AssignmentReadModel]:
        assignments = self.lead_query_service.get_assignment_history(lead_id)
        if assignments is None:
            raise ObjectDoesNotExist(lead_id)
        return assignments

    def get_notes(self, lead_id: str) -> Iterable[NoteReadModel]:
        notes = self.lead_query_service.get_notes(lead_id)
        if notes is None:
            raise ObjectDoesNotExist(lead_id)
        return notes
