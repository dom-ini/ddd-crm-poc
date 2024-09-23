import datetime as dt

import pytest

from sales.domain.value_objects.acquisition_source import AcquisitionSource
from sales.domain.value_objects.note import Note


@pytest.fixture
def source() -> AcquisitionSource:
    return AcquisitionSource(name="ads")


@pytest.fixture()
def note() -> Note:
    return Note(
        created_by_id="salesman_1",
        content="This is a note",
        created_at=dt.datetime.now(),
    )
