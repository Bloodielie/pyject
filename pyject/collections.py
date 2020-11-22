from contextlib import contextmanager
from contextvars import ContextVar
from typing import List, Optional, Any, Union, Type, Dict, Iterator

from pyject.exception import DependencyNotFound
from pyject.annotations import get_annotations_to_implementation
from pyject.models import Scope
from pyject.base import BaseCondition, IResolver, IConditionCollections
from pyject.models import DependencyWrapper


def _get_dependency_wrapper(annotation: Any, implementation: Any, scope: Union[Scope, int]) -> DependencyWrapper:
    annotations = get_annotations_to_implementation(implementation)
    return DependencyWrapper(
        type_=annotation,
        target=implementation,
        annotations=annotations,
        scope=scope,
        cache=implementation if annotations is None else None,
    )


class DependencyStorage:
    def __init__(self):
        self._dependencies: Dict[Any, List[DependencyWrapper]] = {}
        self._context_dependencies: ContextVar[Optional[List[DependencyWrapper]]] = ContextVar(f"_context_storage_{id(self)}")

    def add(self, annotation: Any, implementation: Any, scope: Union[Scope, int]) -> None:
        wrapper = _get_dependency_wrapper(annotation, implementation, scope)

        dependency = self._dependencies.get(annotation, None)
        if dependency is None:
            self._dependencies[annotation] = [wrapper]
        else:
            dependency.append(wrapper)

    def add_context(self, annotation: Any, implementation: Any, scope: Union[Scope, int]) -> None:
        wrapper = _get_dependency_wrapper(annotation, implementation, scope)
        new_context_dependencies = [wrapper]

        context_dependencies = self._context_dependencies.get(None)
        if context_dependencies is None:
            self._context_dependencies.set(new_context_dependencies)
        else:
            new_context_dependencies.extend(context_dependencies)
            self._context_dependencies.set(new_context_dependencies)

    @contextmanager
    def override(
        self,
        annotation: Any,
        implementation: Optional[Union[List[Any], Any]] = None,
        factory: Optional[Union[List[Any], Any]] = None,
        *,
        is_clear_cache: bool = False
    ) -> Iterator[None]:
        implementation = implementation if implementation is not None else []
        implementations = implementation if isinstance(implementation, list) else [implementation]

        factory = factory if factory is not None else []
        factories = factory if isinstance(factory, list) else [factory]

        replaceable_implementation = self._dependencies.get(annotation, None)
        if replaceable_implementation is None:
            raise DependencyNotFound("Dependency not found in container")

        spoofed_implementation = []
        for implementation in implementations:
            spoofed_implementation.append(
                DependencyWrapper(type_=annotation, target=implementation, annotations=None, scope=Scope.SINGLETON)
            )

        for factory in factories:
            spoofed_implementation.append(_get_dependency_wrapper(annotation, factory, Scope.TRANSIENT))

        try:
            if is_clear_cache:
                self.clear_cache()
            self._dependencies[annotation] = spoofed_implementation
            yield
        finally:
            self._dependencies[annotation] = replaceable_implementation

    def clear_cache(self) -> None:
        for dependency_wrappers in self._dependencies.values():
            for dependency_wrapper in dependency_wrappers:
                if dependency_wrapper.annotations is None and dependency_wrapper.cache is not None:
                    continue
                dependency_wrapper.cache = None

    def get_dependencies(self, *, ignore_annotation: Optional[Any] = None) -> Iterator[DependencyWrapper]:
        """Get unresolved iterator object/class"""
        for dependency_wrapper in self._context_dependencies.get([]):  # type: ignore
            yield dependency_wrapper

        for dependency_wrappers in self._dependencies.values():
            for dependency_wrapper in dependency_wrappers:
                if dependency_wrapper.type_ == ignore_annotation:
                    continue
                yield dependency_wrapper

    def get_dependencies_by_annotation(self, annotation: Any) -> List[DependencyWrapper]:
        """Get unresolved object/class by annotation"""
        return self._dependencies.get(annotation, [])

    def __len__(self) -> int:
        return len(self._dependencies) + len(self._context_dependencies.get([]))  # type: ignore


class ConditionCollections(IConditionCollections):
    def __init__(
        self,
        resolver: IResolver,
        conditions: Optional[List[Type[BaseCondition]]] = None,
        default_condition: Optional[Type[BaseCondition]] = None,
    ) -> None:
        self._resolver = resolver

        self._conditions = []
        if conditions is not None:
            for condition in conditions:
                self._conditions.append(self._resolve_condition(condition))
        self._default_condition = self._resolve_condition(default_condition) if default_condition is not None else None

    def add(self, condition: Type[BaseCondition]) -> None:
        """Add a condition to apply it in the dependency solution"""
        self._conditions.append(self._resolve_condition(condition))

    def find(self, typing: Any) -> Optional[Any]:
        """Finding a condition for type and getting attributes"""
        for condition in self._conditions:
            if condition.check_typing(typing):
                return condition.get_attributes(typing)

        if self._default_condition is not None:
            return self._default_condition.get_attributes(typing)
        return None

    def _resolve_condition(self, condition: Type[BaseCondition]) -> BaseCondition:
        return condition(self._resolver)

    def __iter__(self) -> Iterator[BaseCondition]:
        for condition in self._conditions:
            yield condition
        if self._default_condition is not None:
            yield self._default_condition

    def __len__(self) -> int:
        if self._default_condition is not None:
            return len(self._conditions) + 1
        return len(self._conditions)
