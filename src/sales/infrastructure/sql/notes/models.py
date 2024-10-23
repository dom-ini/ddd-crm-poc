import datetime as dt
from typing import Any, Self

from sqlalchemy.orm import Mapped, mapped_column

from building_blocks.infrastructure.sql.db import Base
from sales.domain.value_objects.note import Note


class BaseNoteModel(Base[Note]):
    __abstract__ = True

    created_by_id: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    content: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    created_at: Mapped[dt.datetime] = mapped_column(nullable=False)

    def to_domain(self) -> Note:
        return Note(
            created_by_id=self.created_by_id,
            content=self.content,
            created_at=self.created_at,
        )

    @classmethod
    def from_domain(cls, entity: Note, **kwargs: Any) -> Self:
        raise NotImplementedError
