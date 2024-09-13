from collections.abc import Iterator
from contextlib import contextmanager
import shelve


@contextmanager
def get_read_db(file_path: str) -> Iterator[shelve.Shelf]:
    with shelve.open(file_path, "r") as f:
        yield f


def get_write_db(file_path: str) -> shelve.Shelf:
    return shelve.open(file_path, "c", writeback=True)
