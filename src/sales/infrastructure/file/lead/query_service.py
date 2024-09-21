from collections.abc import Iterable, Iterator

from building_blocks.application.filters import FilterCondition
from building_blocks.infrastructure.file.filters import FileFilterService
from building_blocks.infrastructure.file.io import get_read_db
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.lead.query_service import LeadQueryService
from sales.application.notes.query_model import NoteReadModel
from sales.domain.entities.lead import Lead
from sales.infrastructure.file import config


class LeadFileQueryService(LeadQueryService):
    FilterServiceType = FileFilterService[Lead]

    def __init__(
        self,
        leads_file_path: str = config.LEADS_FILE_PATH,
    ) -> None:
        self._file_path = leads_file_path
        self._filter_service = self.FilterServiceType()

    def _get_single_lead(self, lead_id: str) -> Lead | None:
        with get_read_db(self._file_path) as db:
            lead = db.get(lead_id)
        return lead

    def get(self, lead_id: str) -> LeadReadModel | None:
        lead = self._get_single_lead(lead_id)
        if lead is None:
            return None
        return LeadReadModel.from_domain(lead)

    def get_all(self) -> Iterable[LeadReadModel]:
        with get_read_db(self._file_path) as db:
            all_ids = db.keys()
            leads = [LeadReadModel.from_domain(db.get(id)) for id in all_ids]
        return tuple(leads)

    def get_filtered(self, filters: Iterable[FilterCondition]) -> Iterable[LeadReadModel]:
        with get_read_db(self._file_path) as db:
            all_ids = db.keys()
            leads: Iterator[Lead] = (db.get(id) for id in all_ids)
            filtered_leads = [
                LeadReadModel.from_domain(lead)
                for lead in leads
                if self._filter_service.apply_filters(entity=lead, filters=filters)
            ]
        return tuple(filtered_leads)

    def get_assignment_history(self, lead_id: str) -> Iterable[AssignmentReadModel] | None:
        lead = self._get_single_lead(lead_id)
        if lead is None:
            return None
        assignments = (AssignmentReadModel.from_domain(assignment) for assignment in lead.assignment_history)
        return tuple(assignments)

    def get_notes(self, lead_id: str) -> Iterable[NoteReadModel] | None:
        lead = self._get_single_lead(lead_id)
        if lead is None:
            return None
        notes = (NoteReadModel.from_domain(note) for note in lead.notes_history)
        return tuple(notes)
