from contextvars import ContextVar
from typing import Any, List, Optional, Iterator, Union

from enum import IntEnum
from dataclasses import dataclass

from pyject.utils import _check_annotation


class Scope(IntEnum):
    SINGLETON: int = 0
    TRANSIENT: int = 1


@dataclass(frozen=True)
class DependencyWrapper:
    type_: Any
    target: Any
    scope: int = Scope.TRANSIENT


class DependencyStorage:
    def __init__(self):
        self._dependencies: List[DependencyWrapper] = []
        self._context_dependencies: ContextVar[Optional[List[DependencyWrapper]]] = ContextVar(f"_context_storage_{id(self)}")

    def add(self, annotation: Any, implementation: Any, scope: Union[Scope, int], in_context: bool = False) -> None:
        wrapper = DependencyWrapper(type_=annotation, target=implementation, scope=scope)
        if not in_context:
            self._dependencies.append(wrapper)
        else:
            new_context_dependencies = [wrapper]
            context_dependencies = self._context_dependencies.get(None)
            if context_dependencies is None:
                self._context_dependencies.set(new_context_dependencies)
            else:
                new_context_dependencies.extend(context_dependencies)
                self._context_dependencies.set(new_context_dependencies)

    def get_raw_dependency(self, annotation: Any) -> Iterator[DependencyWrapper]:
        """Get unresolved object/class"""
        context_dependency_storage = self._context_dependencies.get(None)
        if context_dependency_storage is None:
            storages = [self._dependencies]
        else:
            storages = [context_dependency_storage, self._dependencies]

        for storage in storages:
            for dependency_wrapper in storage:
                if _check_annotation(annotation, dependency_wrapper.type_):
                    yield dependency_wrapper

    def __len__(self) -> int:
        return len(self._dependencies) + len(self._context_dependencies.get([]))  # type: ignore
