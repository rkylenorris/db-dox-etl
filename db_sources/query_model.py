import yaml

from pathlib import Path
from typing import Any, Iterator
from dataclasses import dataclass
from functools import cached_property

from collections.abc import Sequence


QUERIES_PATH = Path('db_sources/queries')


@dataclass(frozen=True)
class Query:
    """
    Representation of a database query's metadata.
    Immutable dataclass that holds identifying and descriptive information about a
    query stored on disk.
    Attributes:
        name (str): Logical name or identifier for the query.
        path (str): File-system path (typically relative) to the query file, resolved
            against the module-level QUERIES_PATH constant.
        description (str): Human-readable description of the query's purpose.
        order (int): Integer used to determine ordering (e.g., execution or display order).
    Properties:
        full_path (pathlib.Path): Computed Path obtained by joining QUERIES_PATH with
            this instance's `path`. QUERIES_PATH is a module constant declared at the top.
    Notes:
        - The dataclass is frozen, so instances are immutable.
    """
    name: str
    path: str
    description: str
    order: int

    def __post_init__(self):
        if not self.full_path.exists():
            raise FileNotFoundError(
                f"Query {self.name}'s path ({self.full_path}) does not exist.")

    @cached_property
    def full_path(self) -> Path:
        return QUERIES_PATH / self.path


def _import_queries_from_registry(registry_path: Path = QUERIES_PATH / "registry.yaml") -> list[Query]:

    registry = yaml.safe_load(registry_path.read_text())

    return _flatten_registry(registry)


def _flatten_registry(registry: dict[str, Any]) -> list[Query]:

    queries: list[Query] = []

    for k, v in registry.items():
        if isinstance(v, dict) and "path" in v.keys():
            queries.append(Query(**v))
        elif isinstance(v, dict):
            queries.extend(_flatten_registry(v))

    return queries


class Queries(Sequence[Query]):

    def __init__(self, query_list: list[Query] = _import_queries_from_registry()) -> None:
        self._items = sorted(query_list, key=lambda q: q.order)

    def __getitem__(self, index: int) -> Query:
        return self._items[index]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Query]:
        return iter(self._items)
