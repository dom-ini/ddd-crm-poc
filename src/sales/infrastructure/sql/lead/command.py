from building_blocks.infrastructure.sql.command import BaseSQLUnitOfWork
from sales.application.lead.command import LeadUnitOfWork
from sales.infrastructure.sql.lead.repository import LeadSQLRepository


class LeadSQLUnitOfWork(BaseSQLUnitOfWork, LeadUnitOfWork):
    RepositoryType = LeadSQLRepository
