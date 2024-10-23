from typing import Any, Self

from sqlalchemy.orm import Mapped, mapped_column

from building_blocks.infrastructure.sql.db import Base
from sales.domain.entities.sales_representative import SalesRepresentative


class SalesRepresentativeModel(Base[SalesRepresentative]):
    __tablename__ = "sales_representative"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)

    def to_domain(self) -> SalesRepresentative:
        return SalesRepresentative.reconstitute(id=self.id, first_name=self.first_name, last_name=self.last_name)

    @classmethod
    def from_domain(cls, entity: SalesRepresentative, **kwargs: Any) -> Self:
        return cls(
            id=entity.id,
            first_name=entity.first_name,
            last_name=entity.last_name,
        )
