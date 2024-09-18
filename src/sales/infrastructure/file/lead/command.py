from sales.application.lead.command import LeadUnitOfWork
from sales.infrastructure.file.lead.repository import LeadFileRepository
from building_blocks.infrastructure.file.command import BaseFileUnitOfWork


class LeadFileUnitOfWork(BaseFileUnitOfWork, LeadUnitOfWork):
    Repository = LeadFileRepository
