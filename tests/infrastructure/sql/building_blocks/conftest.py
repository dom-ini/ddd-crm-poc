import pytest

from building_blocks.infrastructure.sql.filters import SQLFilterService


@pytest.fixture()
def filter_service() -> SQLFilterService:
    return SQLFilterService()
