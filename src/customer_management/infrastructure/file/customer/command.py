from building_blocks.infrastructure.file.command import BaseFileUnitOfWork
from customer_management.application.command import CustomerUnitOfWork
from customer_management.infrastructure.file.customer.repository import CustomerFileRepository


class CustomerFileUnitOfWork(BaseFileUnitOfWork, CustomerUnitOfWork):
    RepositoryType = CustomerFileRepository
