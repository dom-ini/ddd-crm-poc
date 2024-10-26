import pytest
from pydantic import Field

from building_blocks.application.nested_model import NestedModel

FIELD_ALIAS = "some_field"
FIELD_EXAMPLE = "some_value_1"


class CustomNestedModel(NestedModel):
    some_field: str = Field(alias=FIELD_ALIAS, examples=[FIELD_EXAMPLE])


@pytest.fixture()
def model_class() -> type[CustomNestedModel]:
    return CustomNestedModel


@pytest.fixture()
def field_alias() -> str:
    return FIELD_ALIAS


@pytest.fixture()
def field_example() -> str:
    return FIELD_EXAMPLE


def test_get_examples(model_class: type[CustomNestedModel], field_alias: str, field_example: str) -> None:
    computed_examples = model_class.get_examples()

    assert computed_examples == {field_alias: field_example}
