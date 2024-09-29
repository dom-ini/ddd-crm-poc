import pytest


@pytest.fixture(scope="session")
def note_content() -> str:
    return "This is a note"
