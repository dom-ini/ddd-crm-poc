import pytest

from containers.config import ContainerManager

ENGINE_NAME = "ENGINE_NAME"


class DummyApplicationContainer:
    pass


class CustomContainerManager(ContainerManager):
    _factory = {ENGINE_NAME: DummyApplicationContainer}


@pytest.fixture()
def container_manager() -> type[ContainerManager]:
    return CustomContainerManager


@pytest.fixture()
def app_container_class() -> type[DummyApplicationContainer]:
    return DummyApplicationContainer


@pytest.fixture()
def engine_name() -> str:
    return ENGINE_NAME


def test_container_manager_correctly_builds_container(
    container_manager: type[ContainerManager],
    app_container_class: type[DummyApplicationContainer],
    engine_name: str,
) -> None:
    container = container_manager.build(engine_name)

    assert isinstance(container, app_container_class)


def test_build_with_invalid_persistence_engine_should_fail(
    container_manager: type[ContainerManager],
) -> None:
    with pytest.raises(ValueError):
        container_manager.build("invalid engine")
