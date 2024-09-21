from collections.abc import Iterable

from attrs import define, field

from building_blocks.domain.entity import EntityWithoutId
from building_blocks.domain.utils.date import get_current_timestamp
from sales.domain.value_objects.lead_assignment_entry import LeadAssignmentEntry

AssignmentHistory = Iterable[LeadAssignmentEntry]


@define(eq=False, kw_only=True)
class LeadAssignments(EntityWithoutId):
    _history: AssignmentHistory = field(alias="history", factory=tuple)

    @property
    def currently_assigned_salesman_id(self) -> str | None:
        most_recent = self.most_recent
        if most_recent is None:
            return None
        return most_recent.new_owner_id

    @property
    def history(self) -> AssignmentHistory:
        return self._history

    @property
    def most_recent(self) -> LeadAssignmentEntry | None:
        if len(self.history) == 0:
            return None
        return self.history[-1]

    def change_assigned_salesman(self, new_salesman_id: str, requestor_id: str) -> None:
        assigned_from = self.currently_assigned_salesman_id
        assignment = self._create_lead_assignment(
            previous_salesman_id=assigned_from,
            new_salesman_id=new_salesman_id,
            requestor_id=requestor_id,
        )
        self._history = self._history + (assignment,)

    def _create_lead_assignment(
        self, previous_salesman_id: str, new_salesman_id: str, requestor_id: str
    ) -> LeadAssignmentEntry:
        return LeadAssignmentEntry(
            previous_owner_id=previous_salesman_id,
            new_owner_id=new_salesman_id,
            assigned_by_id=requestor_id,
            assigned_at=get_current_timestamp(),
        )

    def __str__(self) -> str:
        return f'Currenty assigned salesman: "{self.currently_assigned_salesman_id}"'
