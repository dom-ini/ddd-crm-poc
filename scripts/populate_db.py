from importlib import import_module

import click

ALLOWED_PERSISTENCE_ENGINES = ["sql", "file"]


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("persistence_engine", type=click.Choice(ALLOWED_PERSISTENCE_ENGINES, case_sensitive=False))
def populate_db(persistence_engine: str) -> None:
    """Populate database with example data."""
    module_name = f"fixtures.{persistence_engine}"
    import_module(module_name)


if __name__ == "__main__":
    cli()
