from sales.domain.exceptions import CanCreateOnlyOneLeadPerCustomer, LeadCanBeCreatedOnlyForInitialCustomer
from sales.domain.repositories.lead import LeadRepository
from sales.domain.service.shared import SalesCustomerStatusName


def ensure_one_lead_per_customer(lead_repo: LeadRepository, customer_id: str) -> None:
    if lead_repo.get_by_customer(customer_id) is not None:
        raise CanCreateOnlyOneLeadPerCustomer


def ensure_customer_has_initial_status(status: str) -> None:
    if status != SalesCustomerStatusName.INITIAL:
        raise LeadCanBeCreatedOnlyForInitialCustomer
