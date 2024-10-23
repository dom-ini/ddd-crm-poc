from building_blocks.infrastructure.sql.command import BaseSQLUnitOfWork
from sales.application.opportunity.command import OpportunityUnitOfWork
from sales.infrastructure.sql.opportunity.repository import OpportunitySQLRepository


class OpportunitySQLUnitOfWork(BaseSQLUnitOfWork, OpportunityUnitOfWork):
    RepositoryType = OpportunitySQLRepository
