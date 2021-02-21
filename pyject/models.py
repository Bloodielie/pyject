from typing import Any, Optional, Tuple

from enum import IntEnum
from dataclasses import dataclass


class Scope(IntEnum):
    SINGLETON: int = 0
    TRANSIENT: int = 1
    CONTEXT: int = 2


@dataclass
class DependencyWrapper:
    type_: Any
    target: Any
    annotations: Optional[Tuple[Tuple[str, Any]]] = None
    scope: int = Scope.TRANSIENT
    cache: Optional[Any] = None
    type_arguments: Tuple = ()
