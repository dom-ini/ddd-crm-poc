from collections.abc import Iterable

from building_blocks.application.exceptions import ObjectDoesNotExist
from building_blocks.application.filters import FilterCondition, FilterConditionType
from sales.application.notes.query_model import NoteReadModel
from sales.application.opportunity.query_model import OfferItemReadModel, OpportunityReadModel
from sales.application.opportunity.query_service import OpportunityQueryService


class OpportunityQueryUseCase:
    def __init__(self, opportunity_query_service: OpportunityQueryService) -> None:
        self.opportunity_query_service = opportunity_query_service

    def get(self, opportunity_id: str) -> OpportunityReadModel:
        opportunity = self.opportunity_query_service.get(opportunity_id)
        if opportunity is None:
            raise ObjectDoesNotExist(opportunity_id)
        return opportunity

    def get_all(self) -> Iterable[OpportunityReadModel]:
        opportunites = self.opportunity_query_service.get_all()
        return opportunites

    def get_filtered(
        self,
        stage: str | None = None,
        priority: str | None = None,
        customer_id: str | None = None,
        owner_id: str | None = None,
    ) -> Iterable[OpportunityReadModel]:
        filters = [
            FilterCondition(
                field="stage.name",
                value=stage,
                condition_type=FilterConditionType.EQUALS,
            ),
            FilterCondition(
                field="priority.level",
                value=priority,
                condition_type=FilterConditionType.EQUALS,
            ),
            FilterCondition(
                field="customer_id",
                value=customer_id,
                condition_type=FilterConditionType.EQUALS,
            ),
            FilterCondition(
                field="owner_id",
                value=owner_id,
                condition_type=FilterConditionType.EQUALS,
            ),
        ]
        opportunities = self.opportunity_query_service.get_filtered(filters)
        return opportunities

    def get_notes(self, opportunity_id: str) -> Iterable[NoteReadModel]:
        notes = self.opportunity_query_service.get_notes(opportunity_id)
        if notes is None:
            raise ObjectDoesNotExist(opportunity_id)
        return notes

    def get_offer(self, opportunity_id: str) -> Iterable[OfferItemReadModel]:
        offer = self.opportunity_query_service.get_offer(opportunity_id)
        if offer is None:
            raise ObjectDoesNotExist(opportunity_id)
        return offer
