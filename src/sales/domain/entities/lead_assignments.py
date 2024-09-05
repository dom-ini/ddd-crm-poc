from uuid import UUID
from attrs import define, field
from building_blocks.domain.entity import EntityWithoutId
from building_blocks.domain.utils.date import get_current_timestamp
from sales.domain.value_objects.lead_assignment_entry import LeadAssignmentEntry

AssignmentHistory = tuple[LeadAssignmentEntry]


@define(eq=False, kw_only=True)
class LeadAssignments(EntityWithoutId):
    _history: AssignmentHistory = field(alias="history", factory=tuple)

    @property
    def currently_assigned_salesman_id(self) -> UUID | None:
        if not len(self.history):
            return None
        return self._history[-1].new_owner_id

    @property
    def history(self) -> AssignmentHistory:
        return self._history

    def change_assigned_salesman(
        self, new_salesman_id: UUID, requestor_id: UUID
    ) -> None:
        assigned_from = self.currently_assigned_salesman_id
        assignment = self._create_lead_assignment(
            previous_salesman_id=assigned_from,
            new_salesman_id=new_salesman_id,
            requestor_id=requestor_id,
        )
        self._history = self._history + (assignment,)

    def _create_lead_assignment(
        self, previous_salesman_id: UUID, new_salesman_id: UUID, requestor_id: UUID
    ) -> LeadAssignmentEntry:
        return LeadAssignmentEntry(
            previous_owner_id=previous_salesman_id,
            new_owner_id=new_salesman_id,
            assigned_by_id=requestor_id,
            assigned_at=get_current_timestamp(),
        )

    def __str__(self) -> str:
        return f'Currenty assigned salesman: "{self.currently_assigned_salesman_id}"'
