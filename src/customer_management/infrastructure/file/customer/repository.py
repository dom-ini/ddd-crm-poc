import shelve
from customer_management.domain.repositories.customer import CustomerRepository
from customer_management.domain.entities.customer import Customer
from building_blocks.infrastructure.exceptions import (
    ObjectAlreadyExists,
)


class CustomerFileRepository(CustomerRepository):
    def __init__(self, db: shelve.Shelf) -> None:
        self.db = db

    def get(self, customer_id: str) -> Customer | None:
        customer = self.db.get(customer_id)
        return customer

    def create(self, customer: Customer) -> None:
        if customer.id in self.db:
            raise ObjectAlreadyExists(f"Customer with id={customer.id} already exists")
        self.db[customer.id] = customer

    def update(self, customer: Customer) -> None:
        self.db[customer.id] = customer
