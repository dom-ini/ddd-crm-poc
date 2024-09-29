from pathlib import Path
from uuid import uuid4

import pytest

TEST_DATA_FOLDER = Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def salesman_1_id() -> str:
    return str(uuid4())


@pytest.fixture(scope="session")
def salesman_2_id() -> str:
    return str(uuid4())
