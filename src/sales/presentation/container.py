from typing import Protocol

from fastapi import Request

from authentication.infrastructure.service.base import AuthenticationService
from building_blocks.infrastructure.vo_service import ValueObjectService
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

    auth_service: AuthenticationService

    currency_vo_service: ValueObjectService
    product_vo_service: ValueObjectService


def get_container(request: Request) -> SalesApplicationContainer:
    return request.app.state.container
