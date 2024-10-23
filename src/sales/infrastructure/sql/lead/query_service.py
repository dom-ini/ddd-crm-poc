from collections.abc import Iterable, Sequence

from sqlalchemy import select

from building_blocks.application.filters import FilterCondition
from building_blocks.infrastructure.sql.db import SessionFactory
from building_blocks.infrastructure.sql.filters import SQLFilterService
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.lead.query_service import LeadQueryService
from sales.application.notes.query_model import NoteReadModel
from sales.domain.entities.lead import Lead
from sales.infrastructure.sql.lead.models import LeadAssignmentEntryModel, LeadModel, LeadNoteModel


class LeadSQLQueryService(LeadQueryService):
    FilterServiceType = SQLFilterService

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory
        self._filter_service = self.FilterServiceType()

    def _get_single_lead(self, lead_id: str) -> Lead | None:
        query = select(LeadModel).where(LeadModel.id == lead_id)
        with self._session_factory() as db:
            lead = db.scalar(query)
            if lead is None:
                return None
            return lead.to_domain()

    def get(self, lead_id: str) -> LeadReadModel | None:
        lead = self._get_single_lead(lead_id)
        if lead is None:
            return None
        return LeadReadModel.from_domain(lead)

    def get_all(self) -> Sequence[LeadReadModel]:
        query = select(LeadModel)
        with self._session_factory() as db:
            leads = tuple(lead.to_domain() for lead in db.scalars(query))
        return tuple(LeadReadModel.from_domain(lead) for lead in leads)

    def get_filtered(self, filters: Iterable[FilterCondition]) -> Sequence[LeadReadModel]:
        base_query = select(LeadModel)
        query = self._filter_service.get_query_with_filters(
            model=LeadModel,
            base_query=base_query,
            filters=filters,
        )
        with self._session_factory() as db:
            leads = tuple(lead.to_domain() for lead in db.scalars(query))
        return tuple(LeadReadModel.from_domain(lead) for lead in leads)

    def get_assignment_history(self, lead_id: str) -> Sequence[AssignmentReadModel] | None:
        return self._get_lead_children_entries(
            lead_id=lead_id,
            read_model=AssignmentReadModel,
            db_model=LeadAssignmentEntryModel,
        )

    def get_notes(self, lead_id: str) -> Sequence[NoteReadModel] | None:
        return self._get_lead_children_entries(lead_id=lead_id, read_model=NoteReadModel, db_model=LeadNoteModel)

    def _get_lead_children_entries[
        ReadModelT, DBModelT
    ](self, lead_id: str, read_model: ReadModelT, db_model: DBModelT) -> Sequence[ReadModelT]:
        lead = self._get_single_lead(lead_id)
        if lead is None:
            return None
        query = select(db_model).where(db_model.lead_id == lead_id)
        with self._session_factory() as db:
            entries = tuple(entry.to_domain() for entry in db.scalars(query))
        return tuple(read_model.from_domain(entry) for entry in entries)
