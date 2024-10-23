from firebase_admin import credentials

from authentication.infrastructure import config as auth_config
from authentication.infrastructure.service.firebase import FirebaseAuthenticationService
from building_blocks.infrastructure.file.vo_service import FileValueObjectService
from containers.container import ApplicationContainer
from customer_management.application.acl import OpportunityService, SalesRepresentativeService
from customer_management.application.query_model import CountryReadModel, LanguageReadModel
from customer_management.infrastructure.file import config as customer_config
from customer_management.infrastructure.file.customer.command import CustomerFileUnitOfWork
from customer_management.infrastructure.file.customer.query_service import CustomerFileQueryService
from sales.application.acl import CustomerService
from sales.application.opportunity.query_model import CurrencyReadModel, ProductReadModel
from sales.infrastructure.file import config as sales_config
from sales.infrastructure.file.lead.command import LeadFileUnitOfWork
from sales.infrastructure.file.lead.query_service import LeadFileQueryService
from sales.infrastructure.file.opportunity.command import OpportunityFileUnitOfWork
from sales.infrastructure.file.opportunity.query_service import OpportunityFileQueryService
from sales.infrastructure.file.sales_representative.command import SalesRepresentativeFileUnitOfWork
from sales.infrastructure.file.sales_representative.query_service import SalesRepresentativeFileQueryService


class FileApplicationContainer(ApplicationContainer):
    def __init__(self) -> None:
        firebase_credentials = credentials.Certificate(auth_config.FIREBASE_SERVICE_KEY_PATH)
        self._auth_service = FirebaseAuthenticationService(firebase_credentials)

        self._customer_uow = CustomerFileUnitOfWork(customer_config.CUSTOMERS_PATH)
        self._lead_uow = LeadFileUnitOfWork(sales_config.LEAD_PATH)
        self._opportunity_uow = OpportunityFileUnitOfWork(sales_config.OPPORTUNITIES_PATH)
        self._sr_uow = SalesRepresentativeFileUnitOfWork(sales_config.SALES_REPR_PATH)

        self._customer_service = CustomerService(customer_uow=self._customer_uow)
        self._sr_service = SalesRepresentativeService(salesman_uow=self._sr_uow)
        self._opportunity_service = OpportunityService(opportunity_uow=self._opportunity_uow)

        self._customer_qs = CustomerFileQueryService(customer_config.CUSTOMERS_PATH)
        self._lead_qs = LeadFileQueryService(sales_config.LEAD_PATH)
        self._opportunity_qs = OpportunityFileQueryService(sales_config.OPPORTUNITIES_PATH)
        self._sr_qs = SalesRepresentativeFileQueryService(sales_config.SALES_REPR_PATH)

        self.language_vo_service = FileValueObjectService(
            file_path=customer_config.LANGUAGES_PATH, read_model=LanguageReadModel
        )
        self.country_vo_service = FileValueObjectService(
            file_path=customer_config.COUNTRIES_PATH, read_model=CountryReadModel
        )
        self.currency_vo_service = FileValueObjectService(
            file_path=sales_config.CURRENCIES_PATH, read_model=CurrencyReadModel
        )
        self.product_vo_service = FileValueObjectService(
            file_path=sales_config.PRODUCTS_PATH, read_model=ProductReadModel
        )
