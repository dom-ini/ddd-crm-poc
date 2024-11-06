from collections.abc import Iterator
from pathlib import Path

import pytest

FILE_TEST_DATA_FOLDER = Path(__file__).parent.parent.parent / "infrastructure/file/test_data"
FILE_LEAD_TEST_DATA_PATH = FILE_TEST_DATA_FOLDER / "test-lead"
FILE_CUSTOMER_TEST_DATA_PATH = FILE_TEST_DATA_FOLDER / "test-customer"
FILE_OPPORTUNITY_TEST_DATA_PATH = FILE_TEST_DATA_FOLDER / "test-opportunity"
FILE_SALES_REPRESENTATIVE_TEST_DATA_PATH = FILE_TEST_DATA_FOLDER / "test-sales-representative"
FILE_VO_TEST_DATA_PATH = FILE_TEST_DATA_FOLDER / "test-vo"


@pytest.fixture(scope="session", autouse=True)
def clear_file_test_data() -> Iterator[None]:
    yield
    for file in FILE_TEST_DATA_FOLDER.iterdir():
        file.unlink()
