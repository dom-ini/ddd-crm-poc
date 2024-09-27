from building_blocks.infrastructure.file.command import BaseFileUnitOfWork
from sales.application.opportunity.command import OpportunityUnitOfWork
from sales.infrastructure.file.opportunity.repository import OpportunityFileRepository


class OpportunityFileUnitOfWork(BaseFileUnitOfWork, OpportunityUnitOfWork):
    RepositoryType = OpportunityFileRepository
