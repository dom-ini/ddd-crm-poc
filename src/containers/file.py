import os

from firebase_admin import credentials

from authentication.infrastructure.service.firebase import FirebaseAuthenticationService
from containers.container import ApplicationContainer
from customer_management.application.acl import OpportunityService, SalesRepresentativeService
from customer_management.infrastructure.file.config import CUSTOMERS_FILE_PATH
from customer_management.infrastructure.file.customer.command import CustomerFileUnitOfWork
from customer_management.infrastructure.file.customer.query_service import CustomerFileQueryService
from sales.application.acl import CustomerService
from sales.infrastructure.file.config import LEADS_FILE_PATH, OPPORTUNITIES_FILE_PATH, SALES_REPR_FILE_PATH
from sales.infrastructure.file.lead.command import LeadFileUnitOfWork
from sales.infrastructure.file.lead.query_service import LeadFileQueryService
from sales.infrastructure.file.opportunity.command import OpportunityFileUnitOfWork
from sales.infrastructure.file.opportunity.query_service import OpportunityFileQueryService
from sales.infrastructure.file.sales_representative.command import SalesRepresentativeFileUnitOfWork
from sales.infrastructure.file.sales_representative.query_service import SalesRepresentativeFileQueryService


class FileApplicationContainer(ApplicationContainer):
    def __init__(self) -> None:
        firebase_credentials = credentials.Certificate(os.getenv("FIREBASE_SERVICE_KEY_PATH"))
        self._auth_service = FirebaseAuthenticationService(firebase_credentials)

        self._customer_uow = CustomerFileUnitOfWork(CUSTOMERS_FILE_PATH)
        self._lead_uow = LeadFileUnitOfWork(LEADS_FILE_PATH)
        self._opportunity_uow = OpportunityFileUnitOfWork(OPPORTUNITIES_FILE_PATH)
        self._sr_uow = SalesRepresentativeFileUnitOfWork(SALES_REPR_FILE_PATH)

        self._customer_service = CustomerService(customer_uow=self._customer_uow)
        self._sr_service = SalesRepresentativeService(salesman_uow=self._sr_uow)
        self._opportunity_service = OpportunityService(opportunity_uow=self._opportunity_uow)

        self._customer_qs = CustomerFileQueryService(CUSTOMERS_FILE_PATH)
        self._lead_qs = LeadFileQueryService(LEADS_FILE_PATH)
        self._opportunity_qs = OpportunityFileQueryService(OPPORTUNITIES_FILE_PATH)
        self._sr_qs = SalesRepresentativeFileQueryService(SALES_REPR_FILE_PATH)
