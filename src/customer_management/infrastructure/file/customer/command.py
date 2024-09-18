from customer_management.application.command import CustomerUnitOfWork
from customer_management.infrastructure.file.customer.repository import (
    CustomerFileRepository,
)
from building_blocks.infrastructure.file.command import BaseFileUnitOfWork


class CustomerFileUnitOfWork(BaseFileUnitOfWork, CustomerUnitOfWork):
    Repository = CustomerFileRepository
