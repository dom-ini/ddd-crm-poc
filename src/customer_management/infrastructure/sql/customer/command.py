from building_blocks.infrastructure.sql.command import BaseSQLUnitOfWork
from customer_management.application.command import CustomerUnitOfWork
from customer_management.infrastructure.sql.customer.repository import CustomerSQLRepository


class CustomerSQLUnitOfWork(BaseSQLUnitOfWork, CustomerUnitOfWork):
    RepositoryType = CustomerSQLRepository
