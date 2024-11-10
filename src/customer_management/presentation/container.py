from typing import Protocol

from building_blocks.infrastructure.vo_service import ValueObjectService
from customer_management.application.command import CustomerCommandUseCase
from customer_management.application.query import CustomerQueryUseCase


class CustomerManagementApplicationContainer(Protocol):
    customer_command_use_case: CustomerCommandUseCase
    customer_query_use_case: CustomerQueryUseCase

    language_vo_service: ValueObjectService
    country_vo_service: ValueObjectService
