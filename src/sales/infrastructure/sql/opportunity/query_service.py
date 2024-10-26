from collections.abc import Iterable, Sequence

from sqlalchemy import select

from building_blocks.application.filters import FilterCondition
from building_blocks.infrastructure.sql.db import SessionFactory
from building_blocks.infrastructure.sql.filters import SQLFilterService
from sales.application.notes.query_model import NoteReadModel
from sales.application.opportunity.query_model import OfferItemReadModel, OpportunityReadModel
from sales.application.opportunity.query_service import OpportunityQueryService
from sales.domain.entities.opportunity import Opportunity
from sales.infrastructure.sql.opportunity.models import OfferItemModel, OpportunityModel, OpportunityNoteModel

ReadModelT = type[OfferItemReadModel] | type[NoteReadModel]
DBModelT = type[OfferItemModel] | type[OpportunityNoteModel]


class OpportunitySQLQueryService(OpportunityQueryService):
    FilterServiceType = SQLFilterService

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory
        self._filter_service = self.FilterServiceType()

    def _get_single_opportunity(self, opportunity_id: str) -> Opportunity | None:
        query = select(OpportunityModel).where(OpportunityModel.id == opportunity_id)
        with self._session_factory() as db:
            opportunity = db.scalar(query)
            if opportunity is None:
                return None
            return opportunity.to_domain()

    def get(self, opportunity_id: str) -> OpportunityReadModel | None:
        opportunity = self._get_single_opportunity(opportunity_id)
        if opportunity is None:
            return None
        return OpportunityReadModel.from_domain(opportunity)

    def get_all(self) -> Sequence[OpportunityReadModel]:
        query = select(OpportunityModel)
        with self._session_factory() as db:
            opportunities = tuple(opportunity.to_domain() for opportunity in db.scalars(query))
        return tuple(OpportunityReadModel.from_domain(opportunity) for opportunity in opportunities)

    def get_filtered(self, filters: Iterable[FilterCondition]) -> Sequence[OpportunityReadModel]:
        base_query = select(OpportunityModel)
        query = self._filter_service.get_query_with_filters(
            model=OpportunityModel,
            base_query=base_query,
            filters=filters,
        )
        with self._session_factory() as db:
            opportunities = tuple(opportunity.to_domain() for opportunity in db.scalars(query))
        return tuple(OpportunityReadModel.from_domain(opportunity) for opportunity in opportunities)

    def get_notes(self, opportunity_id: str) -> Sequence[NoteReadModel] | None:
        return self._get_opportunity_children_entries(
            opportunity_id=opportunity_id,
            read_model=NoteReadModel,
            db_model=OpportunityNoteModel,
        )

    def get_offer(self, opportunity_id: str) -> Sequence[OfferItemReadModel] | None:
        return self._get_opportunity_children_entries(
            opportunity_id=opportunity_id,
            read_model=OfferItemReadModel,
            db_model=OfferItemModel,
        )

    def _get_opportunity_children_entries(
        self, opportunity_id: str, read_model: ReadModelT, db_model: DBModelT
    ) -> Sequence[ReadModelT] | None:
        opportunity = self._get_single_opportunity(opportunity_id)
        if opportunity is None:
            return None
        query = select(db_model).where(db_model.opportunity_id == opportunity_id)
        with self._session_factory() as db:
            entries = tuple(entry.to_domain() for entry in db.scalars(query))
        return tuple(read_model.from_domain(entry) for entry in entries)
