from typing import Protocol

from building_blocks.presentation.cli.renderer import Renderer


class CliContext[ContainerT](Protocol):
    container: ContainerT
    renderer: Renderer
