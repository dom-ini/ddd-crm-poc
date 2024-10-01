from sales.domain.exceptions import OpportunityCanBeCreatedOnlyForConvertedCustomer
from sales.domain.service.shared import SalesCustomerStatusName


def ensure_customer_has_converted_status(status: str) -> None:
    if status != SalesCustomerStatusName.CONVERTED:
        raise OpportunityCanBeCreatedOnlyForConvertedCustomer
