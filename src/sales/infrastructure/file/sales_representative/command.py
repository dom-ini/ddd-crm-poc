from building_blocks.infrastructure.file.command import BaseFileUnitOfWork
from sales.application.sales_representative.command import SalesRepresentativeUnitOfWork
from sales.infrastructure.file.sales_representative.repository import SalesRepresentativeFileRepository


class SalesRepresentativeFileUnitOfWork(BaseFileUnitOfWork, SalesRepresentativeUnitOfWork):
    RepositoryType = SalesRepresentativeFileRepository
