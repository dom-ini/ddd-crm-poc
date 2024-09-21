from typing import Any, Callable, Iterable, TypeVar

ItemT = TypeVar("ItemT")
ItemCallback = Callable[[ItemT], Any]


def get_duplicates(values: Iterable[ItemT], value_callback: ItemCallback = lambda x: x) -> Iterable[ItemT]:
    seen = set()
    duplicates = set()
    for item in values:
        transformed = value_callback(item)
        if transformed in seen:
            duplicates.add(item)
        seen.add(transformed)
    return tuple(duplicates)
