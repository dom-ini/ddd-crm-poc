from collections.abc import Iterable, Sequence

from sqlalchemy import select

from building_blocks.application.filters import FilterCondition
from building_blocks.infrastructure.sql.db import SessionFactory
from building_blocks.infrastructure.sql.filters import SQLFilterService
from customer_management.application.query_model import ContactPersonReadModel, CustomerReadModel
from customer_management.application.query_service import CustomerQueryService
from customer_management.domain.entities.customer import Customer
from customer_management.infrastructure.sql.customer.models import ContactPersonModel, CustomerModel


class CustomerSQLQueryService(CustomerQueryService):
    FilterServiceType = SQLFilterService

    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory
        self._filter_service = self.FilterServiceType()

    def _get_single_customer(self, customer_id: str) -> Customer | None:
        query = select(CustomerModel).where(CustomerModel.id == customer_id)
        with self._session_factory() as db:
            customer = db.scalar(query)
            if customer is None:
                return None
            return customer.to_domain()

    def get(self, customer_id: str) -> CustomerReadModel | None:
        customer = self._get_single_customer(customer_id)
        if customer is None:
            return None
        return CustomerReadModel.from_domain(customer)

    def get_all(self) -> Sequence[CustomerReadModel]:
        query = select(CustomerModel)
        with self._session_factory() as db:
            customers = tuple(customer.to_domain() for customer in db.scalars(query))
        return tuple(CustomerReadModel.from_domain(customer) for customer in customers)

    def get_filtered(self, filters: Iterable[FilterCondition]) -> Sequence[CustomerReadModel]:
        base_query = select(CustomerModel)
        query = self._filter_service.get_query_with_filters(
            model=CustomerModel,
            base_query=base_query,
            filters=filters,
        )
        with self._session_factory() as db:
            customers = tuple(customer.to_domain() for customer in db.scalars(query))
        return tuple(CustomerReadModel.from_domain(customer) for customer in customers)

    def get_contact_persons(self, customer_id: str) -> Sequence[ContactPersonReadModel] | None:
        customer = self._get_single_customer(customer_id)
        if customer is None:
            return None
        query = select(ContactPersonModel).where(ContactPersonModel.customer_id == customer_id)
        with self._session_factory() as db:
            contact_persons = tuple(person.to_domain() for person in db.scalars(query))
        return tuple(ContactPersonReadModel.from_domain(person) for person in contact_persons)
