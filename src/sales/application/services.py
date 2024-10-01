from building_blocks.application.exceptions import InvalidData
from sales.application.acl import ICustomerService
from sales.application.sales_representative.command import SalesRepresentativeUnitOfWork


class CustomerServiceMixin:
    customer_service: ICustomerService

    def _verify_that_customer_exists(self, customer_id: str) -> None:
        if not self.customer_service.customer_exists(customer_id):
            raise InvalidData(f"Customer with id={customer_id} does not exist")


class SalesRepresentativeServiceMixin:
    salesman_uow: SalesRepresentativeUnitOfWork

    def _verify_that_salesman_exists(self, salesman_id: str) -> None:
        with self.salesman_uow as uow:
            salesman = uow.repository.get(representative_id=salesman_id)
        if salesman is None:
            raise InvalidData(f"Sales representative with id={salesman_id} does not exist")
