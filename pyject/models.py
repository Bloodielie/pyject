from typing import Any

from pydantic import BaseModel
from enum import IntEnum


class Scope(IntEnum):
    SINGLETON: int = 0
    TRANSIENT: int = 1


class DependencyWrapper(BaseModel):
    type_: Any
    target: Any
    scope: int = Scope.TRANSIENT
