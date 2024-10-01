from collections.abc import Sequence

from customer_management.application.acl import Opportunity
from customer_management.domain.exceptions import CustomerStillHasNotClosedOpportunities

OPPORTUNITY_CLOSED_STAGE_NAMES = ["closed-won", "closed-lost"]


def ensure_all_opportunities_are_closed(opportunities: Sequence[Opportunity]) -> None:
    for opportunity in opportunities:
        if opportunity.stage_name not in OPPORTUNITY_CLOSED_STAGE_NAMES:
            raise CustomerStillHasNotClosedOpportunities
