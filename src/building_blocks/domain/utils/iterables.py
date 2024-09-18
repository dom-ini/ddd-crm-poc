from typing import Any, Callable, Iterable, TypeVar

ItemType = TypeVar("Item")
ItemCallback = Callable[[ItemType], Any]


def get_duplicates(
    values: Iterable[ItemType], value_callback: ItemCallback = lambda x: x
) -> Iterable[ItemType]:
    seen = set()
    duplicates = set()
    for item in values:
        transformed = value_callback(item)
        if transformed in seen:
            duplicates.add(item)
        seen.add(transformed)
    return tuple(duplicates)
