from collections.abc import Iterable, Iterator
from building_blocks.application.filters import FilterCondition
from building_blocks.infrastructure.file.filters import FileFilterService
from building_blocks.infrastructure.file.io import get_read_db
from sales.application.notes.query_model import NoteReadModel
from sales.application.opportunity.query_model import (
    OfferItemReadModel,
    OpportunityReadModel,
)
from sales.application.opportunity.query_service import OpportunityQueryService
from sales.domain.entities.opportunity import Opportunity
from sales.infrastructure.file import config


class OpportunityFileQueryService(OpportunityQueryService):
    FilterServiceType = FileFilterService[Opportunity]

    def __init__(
        self,
        opportunities_file_path: str = config.OPPORTUNITIES_FILE_PATH,
    ) -> None:
        self._file_path = opportunities_file_path
        self._filter_service = self.FilterServiceType()

    def _get_single_opportunity(self, opportunity_id: str) -> Opportunity | None:
        with get_read_db(self._file_path) as db:
            opportunity = db.get(opportunity_id)
        return opportunity

    def get(self, opportunity_id: str) -> OpportunityReadModel | None:
        opportunity = self._get_single_opportunity(opportunity_id)
        if opportunity is None:
            return None
        return OpportunityReadModel.from_domain(opportunity)

    def get_all(self) -> Iterable[OpportunityReadModel]:
        with get_read_db(self._file_path) as db:
            all_ids = db.keys()
            opportunities = [
                OpportunityReadModel.from_domain(db.get(id)) for id in all_ids
            ]
        return tuple(opportunities)

    def get_filtered(
        self, filters: Iterable[FilterCondition]
    ) -> Iterable[OpportunityReadModel]:
        with get_read_db(self._file_path) as db:
            all_ids = db.keys()
            opportunities: Iterator[Opportunity] = (db.get(id) for id in all_ids)
            filtered_opportunities = [
                OpportunityReadModel.from_domain(opportunity)
                for opportunity in opportunities
                if self._filter_service.apply_filters(
                    entity=opportunity, filters=filters
                )
            ]
        return tuple(filtered_opportunities)

    def get_notes(self, opportunity_id: str) -> Iterable[NoteReadModel] | None:
        opportunity = self._get_single_opportunity(opportunity_id)
        if opportunity is None:
            return None
        notes = (NoteReadModel.from_domain(note) for note in opportunity.notes_history)
        return tuple(notes)

    def get_offer(self, opportunity_id: str) -> Iterable[OfferItemReadModel] | None:
        opportunity = self._get_single_opportunity(opportunity_id)
        if opportunity is None:
            return None
        offer = (
            OfferItemReadModel.from_domain(offer_item)
            for offer_item in opportunity.offer
        )
        return tuple(offer)
