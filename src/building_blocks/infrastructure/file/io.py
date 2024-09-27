import shelve
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def get_read_db(file_path: Path) -> Iterator[shelve.Shelf]:
    with shelve.open(file_path, "r") as f:
        yield f


def get_write_db(file_path: Path) -> shelve.Shelf:
    return shelve.open(file_path, "c", writeback=True)
