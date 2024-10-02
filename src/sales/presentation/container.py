from typing import Protocol

from fastapi import Request

from sales.application.lead.command import LeadCommandUseCase
from sales.application.lead.query import LeadQueryUseCase
from sales.application.opportunity.command import OpportunityCommandUseCase
from sales.application.opportunity.query import OpportunityQueryUseCase
from sales.application.sales_representative.command import SalesRepresentativeCommandUseCase
from sales.application.sales_representative.query import SalesRepresentativeQueryUseCase


class SalesApplicationContainer(Protocol):
    lead_command_use_case: LeadCommandUseCase
    lead_query_use_case: LeadQueryUseCase

    sr_command_use_case: SalesRepresentativeCommandUseCase
    sr_query_use_case: SalesRepresentativeQueryUseCase

    opportunity_command_use_case: OpportunityCommandUseCase
    opportunity_query_use_case: OpportunityQueryUseCase


def get_container(request: Request) -> SalesApplicationContainer:
    return request.app.state.container