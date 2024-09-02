from attrs import define
from customer_management.domain.value_objects.company_segment import CompanySegment
from customer_management.domain.value_objects.address import Address
from customer_management.domain.value_objects.industry import Industry
from building_blocks.domain.value_object import ValueObject


@define(frozen=True, kw_only=True)
class CompanyInfo(ValueObject):
    name: str
    industry: Industry
    segment: CompanySegment
    address: Address

    def __str__(self) -> str:
        return self.name
