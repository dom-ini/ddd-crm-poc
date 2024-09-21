from typing import Literal, get_args

from attrs import define, field

from building_blocks.domain.attrs_validators import attrs_value_in
from building_blocks.domain.value_object import ValueObject

CompanySize = Literal["micro", "small", "medium", "large"]
LegalForm = Literal["sole proprietorship", "partnership", "limited", "other"]

ALLOWED_COMPANY_SIZES = get_args(CompanySize)
ALLOWED_LEGAL_FORMS = get_args(LegalForm)


@define(frozen=True, kw_only=True)
class CompanySegment(ValueObject):
    size: CompanySize = field(validator=attrs_value_in(ALLOWED_COMPANY_SIZES))
    legal_form: LegalForm = field(validator=attrs_value_in(ALLOWED_LEGAL_FORMS))

    def __str__(self) -> str:
        return f"Legal form: {self.legal_form}, size: {self.size}"
