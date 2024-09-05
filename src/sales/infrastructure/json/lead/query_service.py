from building_blocks.infrastructure.dto import BaseDTO
from building_blocks.infrastructure.utils.decorators import call_method_before
from building_blocks.infrastructure.utils.comparator import AlwaysTrue
from sales.application.lead.exceptions import LeadDoesNotExist
from sales.application.lead.query_model import AssignmentReadModel, LeadReadModel
from sales.application.lead.query_service import LeadQueryService
from sales.application.notes.query_model import NoteReadModel
from sales.infrastructure.json import config
from sales.infrastructure.json.lead.dto import AssignmentEntryJsonDTO, LeadJsonDTO
from sales.infrastructure.json.notes.dto import NoteJsonDTO
from sales.infrastructure.json.query_service import BaseJsonQueryService


class LeadJsonQueryService(
    LeadQueryService, BaseJsonQueryService[LeadJsonDTO, LeadReadModel]
):
    def __init__(
        self,
        leads_file_path: str = config.LEADS_JSON_FILE_PATH,
        leads_dto_class: type[BaseDTO] = LeadJsonDTO,
        assignment_dto_class: type[BaseDTO] = AssignmentEntryJsonDTO,
        note_dto_class: type[BaseDTO] = NoteJsonDTO,
    ) -> None:
        self._leads_file_path = leads_file_path
        self._assignment_dto_class = assignment_dto_class
        self._note_dto_class = note_dto_class
        super().__init__(dto_class=leads_dto_class)

    def _get_single_lead_dto(self, lead_id: str) -> LeadJsonDTO | None:
        leads = self._get_dto_data(lambda lead: lead.id == lead_id)
        return next(leads, None)

    @call_method_before("_reload_data")
    def get(self, lead_id: str) -> LeadReadModel:
        lead = self._get_single_lead_dto(lead_id)
        if lead is None:
            raise LeadDoesNotExist
        return lead and lead.to_read_model()

    @call_method_before("_reload_data")
    def get_all(self) -> tuple[LeadReadModel]:
        leads = self._get_read_data(lambda _: True)
        return tuple(leads)

    @call_method_before("_reload_data")
    def get_by_customer_and_owner_id(
        self,
        customer_id: str | None = None,
        owner_id: str | None = None,
    ) -> tuple[LeadReadModel, ...]:
        customer_id = customer_id if customer_id is not None else AlwaysTrue()
        owner_id = owner_id if owner_id is not None else AlwaysTrue()
        leads = self._get_read_data(
            lambda lead: lead.customer_id == customer_id
            and lead.assigned_salesman_id == owner_id
        )
        return tuple(leads)

    @call_method_before("_reload_data")
    def get_assignment_history(self, lead_id: str) -> tuple[AssignmentReadModel, ...]:
        lead = self._get_single_lead_dto(lead_id)
        if lead is None:
            raise LeadDoesNotExist
        assignments = (assignment.to_read_model() for assignment in lead.assignments)
        return tuple(assignments)

    @call_method_before("_reload_data")
    def get_notes(self, lead_id: str) -> tuple[NoteReadModel, ...]:
        lead = self._get_single_lead_dto(lead_id)
        if lead is None:
            raise LeadDoesNotExist
        notes = (note.to_read_model() for note in lead.notes)
        return tuple(notes)

    def _reload_data(self) -> None:
        self._load_data_from_file(self._leads_file_path)
