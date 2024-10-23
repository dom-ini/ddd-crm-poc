from abc import ABC

from authentication.infrastructure.service.base import AuthenticationService
from building_blocks.infrastructure.sql.vo_service import SQLValueObjectService
from customer_management.application.acl import OpportunityService, SalesRepresentativeService
from customer_management.application.command import CustomerCommandUseCase, CustomerUnitOfWork
from customer_management.application.query import CustomerQueryUseCase
from customer_management.application.query_service import CustomerQueryService
from sales.application.acl import CustomerService
from sales.application.lead.command import LeadCommandUseCase, LeadUnitOfWork
from sales.application.lead.query import LeadQueryUseCase
from sales.application.lead.query_service import LeadQueryService
from sales.application.opportunity.command import OpportunityCommandUseCase, OpportunityUnitOfWork
from sales.application.opportunity.query import OpportunityQueryUseCase
from sales.application.opportunity.query_service import OpportunityQueryService
from sales.application.sales_representative.command import (
    SalesRepresentativeCommandUseCase,
    SalesRepresentativeUnitOfWork,
)
from sales.application.sales_representative.query import SalesRepresentativeQueryUseCase
from sales.application.sales_representative.query_service import SalesRepresentativeQueryService


class ApplicationContainer(ABC):
    _auth_service: AuthenticationService

    _customer_uow: CustomerUnitOfWork
    _sr_uow: SalesRepresentativeUnitOfWork
    _lead_uow: LeadUnitOfWork
    _opportunity_uow: OpportunityUnitOfWork

    _customer_service: CustomerService
    _sr_service: SalesRepresentativeService
    _opportunity_service: OpportunityService

    _customer_qs: CustomerQueryService
    _sr_qs: SalesRepresentativeQueryService
    _lead_qs: LeadQueryService
    _opportunity_qs: OpportunityQueryService

    language_vo_service: SQLValueObjectService
    country_vo_service: SQLValueObjectService
    currency_vo_service: SQLValueObjectService
    product_vo_service: SQLValueObjectService

    @property
    def customer_command_use_case(self) -> CustomerCommandUseCase:
        return CustomerCommandUseCase(
            customer_uow=self._customer_uow,
            sales_rep_service=self._sr_service,
            opportunity_service=self._opportunity_service,
        )

    @property
    def customer_query_use_case(self) -> CustomerQueryUseCase:
        return CustomerQueryUseCase(customer_query_service=self._customer_qs)

    @property
    def lead_command_use_case(self) -> LeadCommandUseCase:
        return LeadCommandUseCase(
            lead_uow=self._lead_uow,
            salesman_uow=self._sr_uow,
            customer_service=self._customer_service,
        )

    @property
    def lead_query_use_case(self) -> LeadQueryUseCase:
        return LeadQueryUseCase(lead_query_service=self._lead_qs)

    @property
    def opportunity_command_use_case(self) -> OpportunityCommandUseCase:
        return OpportunityCommandUseCase(
            opportunity_uow=self._opportunity_uow,
            salesman_uow=self._sr_uow,
            customer_service=self._customer_service,
        )

    @property
    def opportunity_query_use_case(self) -> OpportunityQueryUseCase:
        return OpportunityQueryUseCase(opportunity_query_service=self._opportunity_qs)

    @property
    def sr_command_use_case(self) -> SalesRepresentativeCommandUseCase:
        return SalesRepresentativeCommandUseCase(sr_uow=self._sr_uow)

    @property
    def sr_query_use_case(self) -> SalesRepresentativeQueryUseCase:
        return SalesRepresentativeQueryUseCase(sr_query_service=self._sr_qs)

    @property
    def auth_service(self) -> AuthenticationService:
        return self._auth_service
