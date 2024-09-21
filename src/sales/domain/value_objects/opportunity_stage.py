from typing import Literal, get_args

from attrs import define, field

from building_blocks.domain.attrs_validators import attrs_value_in
from building_blocks.domain.value_object import ValueObject

OpportunityStageName = Literal["qualification", "proposal", "negotiation", "closed-won", "closed-lost"]
INITIAL_STAGE = "qualification"
ALLOWED_OPPORTUNITY_STAGES = get_args(OpportunityStageName)


@define(frozen=True, kw_only=True)
class OpportunityStage(ValueObject):
    name: OpportunityStageName = field(validator=attrs_value_in(ALLOWED_OPPORTUNITY_STAGES))

    def __str__(self) -> str:
        return self.name
