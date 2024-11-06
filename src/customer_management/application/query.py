from collections.abc import Iterable

from building_blocks.application.exceptions import ObjectDoesNotExist
from building_blocks.application.filters import FilterCondition, FilterConditionType
from customer_management.application.query_model import ContactPersonReadModel, CustomerReadModel
from customer_management.application.query_service import CustomerQueryService


class CustomerQueryUseCase:
    def __init__(self, customer_query_service: CustomerQueryService) -> None:
        self.customer_query_service = customer_query_service

    def get(self, customer_id: str) -> CustomerReadModel:
        customer = self.customer_query_service.get(customer_id)
        if customer is None:
            raise ObjectDoesNotExist(customer_id)
        return customer

    def get_all(self) -> Iterable[CustomerReadModel]:
        customers = self.customer_query_service.get_all()
        return customers

    def get_filtered(
        self,
        relation_manager_id: str | None = None,
        status: str | None = None,
        company_name: str | None = None,
        industry: str | None = None,
        company_size: str | None = None,
        legal_form: str | None = None,
    ) -> Iterable[CustomerReadModel]:
        filters = [
            FilterCondition(
                field="relation_manager_id",
                value=relation_manager_id,
                condition_type=FilterConditionType.EQUALS,
            ),
            FilterCondition(
                field="status.name",
                value=status,
                condition_type=FilterConditionType.EQUALS,
            ),
            FilterCondition(
                field="company_info.name",
                value=company_name,
                condition_type=FilterConditionType.SEARCH,
            ),
            FilterCondition(
                field="company_info.industry.name",
                value=industry,
                condition_type=FilterConditionType.EQUALS,
            ),
            FilterCondition(
                field="company_info.segment.size",
                value=company_size,
                condition_type=FilterConditionType.EQUALS,
            ),
            FilterCondition(
                field="company_info.segment.legal_form",
                value=legal_form,
                condition_type=FilterConditionType.EQUALS,
            ),
        ]
        customers = self.customer_query_service.get_filtered(filters)
        return customers

    def get_contact_persons(self, customer_id: str) -> Iterable[ContactPersonReadModel]:
        contact_persons = self.customer_query_service.get_contact_persons(customer_id)
        if contact_persons is None:
            raise ObjectDoesNotExist(customer_id)
        return contact_persons
