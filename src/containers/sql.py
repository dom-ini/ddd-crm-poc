from firebase_admin import credentials

from authentication.infrastructure import config as auth_config
from authentication.infrastructure.service.firebase import FirebaseAuthenticationService
from building_blocks.infrastructure.sql.db import get_db_session
from building_blocks.infrastructure.sql.vo_service import SQLValueObjectService
from containers.container import ApplicationContainer
from customer_management.application.acl import OpportunityService, SalesRepresentativeService
from customer_management.application.query_model import CountryReadModel, LanguageReadModel
from customer_management.infrastructure.sql.customer.command import CustomerSQLUnitOfWork
from customer_management.infrastructure.sql.customer.models import CountryModel, LanguageModel
from customer_management.infrastructure.sql.customer.query_service import CustomerSQLQueryService
from sales.application.acl import CustomerService
from sales.application.opportunity.query_model import CurrencyReadModel, ProductReadModel
from sales.infrastructure.sql.lead.command import LeadSQLUnitOfWork
from sales.infrastructure.sql.lead.query_service import LeadSQLQueryService
from sales.infrastructure.sql.opportunity.command import OpportunitySQLUnitOfWork
from sales.infrastructure.sql.opportunity.models import CurrencyModel, ProductModel
from sales.infrastructure.sql.opportunity.query_service import OpportunitySQLQueryService
from sales.infrastructure.sql.sales_representative.command import SalesRepresentativeSQLUnitOfWork
from sales.infrastructure.sql.sales_representative.query_service import SalesRepresentativeSQLQueryService


class SQLApplicationContainer(ApplicationContainer):
    def __init__(self) -> None:
        firebase_credentials = credentials.Certificate(auth_config.FIREBASE_SERVICE_KEY_PATH)
        self._auth_service = FirebaseAuthenticationService(firebase_credentials)

        self._customer_uow = CustomerSQLUnitOfWork(get_db_session)
        self._lead_uow = LeadSQLUnitOfWork(get_db_session)
        self._opportunity_uow = OpportunitySQLUnitOfWork(get_db_session)
        self._sr_uow = SalesRepresentativeSQLUnitOfWork(get_db_session)

        self._customer_service = CustomerService(customer_uow=self._customer_uow)
        self._sr_service = SalesRepresentativeService(salesman_uow=self._sr_uow)
        self._opportunity_service = OpportunityService(opportunity_uow=self._opportunity_uow)

        self._customer_qs = CustomerSQLQueryService(get_db_session)
        self._lead_qs = LeadSQLQueryService(get_db_session)
        self._opportunity_qs = OpportunitySQLQueryService(get_db_session)
        self._sr_qs = SalesRepresentativeSQLQueryService(get_db_session)

        self.language_vo_service = SQLValueObjectService(
            session_factory=get_db_session, model=LanguageModel, read_model=LanguageReadModel
        )
        self.country_vo_service = SQLValueObjectService(
            session_factory=get_db_session, model=CountryModel, read_model=CountryReadModel
        )
        self.currency_vo_service = SQLValueObjectService(
            session_factory=get_db_session, model=CurrencyModel, read_model=CurrencyReadModel
        )
        self.product_vo_service = SQLValueObjectService(
            session_factory=get_db_session, model=ProductModel, read_model=ProductReadModel
        )
