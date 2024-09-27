from building_blocks.infrastructure.file.command import BaseFileUnitOfWork
from sales.application.lead.command import LeadUnitOfWork
from sales.infrastructure.file.lead.repository import LeadFileRepository


class LeadFileUnitOfWork(BaseFileUnitOfWork, LeadUnitOfWork):
    RepositoryType = LeadFileRepository
