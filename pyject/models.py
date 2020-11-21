from typing import Any, Optional, Tuple

from enum import IntEnum
from dataclasses import dataclass


class Scope(IntEnum):
    SINGLETON: int = 0
    TRANSIENT: int = 1


@dataclass(frozen=True)
class DependencyWrapper:
    type_: Any
    target: Any
    annotations: Optional[Tuple[Tuple[str, Any]]] = None
    scope: int = Scope.TRANSIENT
