from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Iterable

from building_blocks.application.filters import FilterCondition
from building_blocks.infrastructure.file.filters import FileFilterService
from building_blocks.infrastructure.file.io import get_read_db
from customer_management.application.query_model import ContactPersonReadModel, CustomerReadModel
from customer_management.application.query_service import CustomerQueryService
from customer_management.domain.entities.customer import Customer


class CustomerFileQueryService(CustomerQueryService):
    FilterServiceType = FileFilterService[Customer]

    def __init__(self, customers_file_path: Path) -> None:
        self._file_path = customers_file_path
        self._filter_service = self.FilterServiceType()

    def _get_single_customer(self, customer_id: str) -> Customer | None:
        with get_read_db(self._file_path) as db:
            customer = db.get(customer_id)
        return customer

    def get(self, customer_id: str) -> CustomerReadModel | None:
        customer = self._get_single_customer(customer_id)
        if customer is None:
            return None
        return CustomerReadModel.from_domain(customer)

    def get_all(self) -> Sequence[CustomerReadModel]:
        with get_read_db(self._file_path) as db:
            all_ids = db.keys()
            customers = [CustomerReadModel.from_domain(db.get(id)) for id in all_ids]
        return tuple(customers)

    def get_filtered(self, filters: Iterable[FilterCondition]) -> Sequence[CustomerReadModel]:
        with get_read_db(self._file_path) as db:
            all_ids = db.keys()
            customers: Iterator[Customer] = (db.get(id) for id in all_ids)
            filtered_customers = [
                CustomerReadModel.from_domain(customer)
                for customer in customers
                if self._filter_service.apply_filters(entity=customer, filters=filters)
            ]
        return tuple(filtered_customers)

    def get_contact_persons(self, customer_id: str) -> Sequence[ContactPersonReadModel] | None:
        customer = self._get_single_customer(customer_id)
        if customer is None:
            return None
        contact_persons = (ContactPersonReadModel.from_domain(person) for person in customer.contact_persons)
        return tuple(contact_persons)
