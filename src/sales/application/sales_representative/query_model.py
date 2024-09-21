from typing import Self

from faker import Faker
from pydantic import Field

from building_blocks.application.query_model import BaseReadModel
from sales.domain.entities.sales_representative import SalesRepresentative

faker = Faker(locale="pl_PL")


class SalesRepresentativeReadModel(BaseReadModel[SalesRepresentative]):
    id: str = Field(examples=[faker.uuid4()])
    first_name: str = Field(examples=[faker.first_name()])
    last_name: str = Field(examples=[faker.last_name()])

    @classmethod
    def from_domain(cls, entity: SalesRepresentative) -> Self:
        return cls(id=entity.id, first_name=entity.first_name, last_name=entity.last_name)
