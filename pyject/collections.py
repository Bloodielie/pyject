from typing import List, Optional, Any, Union, Type, Dict, Iterator

from pyject.exception import DependencyNotFound
from pyject.annotations import get_annotations_to_implementation
from pyject.models import Scope
from pyject.base import BaseCondition, IResolver, IConditionCollections
from pyject.models import DependencyWrapper
from pyject.utils import get_typing_args


def _get_dependency_wrapper(annotation: Any, implementation: Any, scope: Union[Scope, int]) -> DependencyWrapper:
    annotations = get_annotations_to_implementation(implementation)
    type_args = get_typing_args(annotation)
    return DependencyWrapper(
        type_=annotation,
        target=implementation,
        annotations=annotations,
        scope=scope,
        cache=implementation if annotations is None else None,
        type_arguments=type_args
    )


def _checking_for_finding_itself_in_annotations(wrapper: DependencyWrapper) -> None:
    error = Exception("Dependency cannot have itself in annotations")
    if not wrapper.type_arguments and wrapper.annotations is not None:
        for annotation in wrapper.annotations:
            annotation_args = get_typing_args(annotation[1])
            if not annotation_args and annotation[1] == wrapper.type_:
                raise error
            else:
                for annotation_arg in annotation_args:
                    if annotation_arg == wrapper.type_:
                        raise error


class DependencyStorageOverrideContext:
    def __init__(
        self,
        dependency_storage: "DependencyStorage",
        annotation: Any,
        spoofed_implementations: List[Any],
        replaceable_implementations: List[Any],
        is_clear_cache: bool = True
    ) -> None:
        self._dependency_storage = dependency_storage
        self._annotation = annotation
        self._spoofed_implementations = spoofed_implementations
        self._replaceable_implementations = replaceable_implementations
        self._is_clear_cache = is_clear_cache

    def __enter__(self) -> None:
        self._dependency_storage._override(
            self._annotation, self._spoofed_implementations, is_clear_cache=self._is_clear_cache
        )

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._dependency_storage._release_overdetermined_dependency(self._annotation, self._replaceable_implementations)

    def __call__(self, *args, **kwargs):
        self._dependency_storage._override(
            self._annotation, self._spoofed_implementations, is_clear_cache=self._is_clear_cache
        )


class DependencyStorage:
    def __init__(self):
        self._dependencies: Dict[Any, List[DependencyWrapper]] = {}

    def _add_dependency(self, wrapper: DependencyWrapper) -> None:
        if wrapper.type_arguments:
            dependency_alias = (wrapper.type_, wrapper.type_arguments)
        else:
            dependency_alias = wrapper.type_

        _checking_for_finding_itself_in_annotations(wrapper)

        dependency = self._dependencies.get(dependency_alias, None)
        if dependency is None:
            self._dependencies[dependency_alias] = [wrapper]
        else:
            dependency.append(wrapper)

    def add_transient(self, annotation: Any, implementation: Any) -> None:
        self._add_dependency(
            _get_dependency_wrapper(annotation, implementation, Scope.TRANSIENT)
        )

    def add_singleton(self, annotation: Any, implementation: Any) -> None:
        self._add_dependency(
            _get_dependency_wrapper(annotation, implementation, Scope.SINGLETON)
        )

    def add_context(self, annotation: Any, implementation: Any) -> None:
        self._add_dependency(
            _get_dependency_wrapper(annotation, implementation, Scope.CONTEXT)
        )

    def add_constant(self, annotation: Any, implementation: Any) -> None:
        wrapper = _get_dependency_wrapper(annotation, implementation, Scope.SINGLETON)
        wrapper.cache = implementation
        self._add_dependency(wrapper)

    def override(
        self,
        annotation: Any,
        implementation: Optional[Union[List[Any], Any]] = None,
        factory: Optional[Union[List[Any], Any]] = None,
        *,
        is_clear_cache: bool = True
    ) -> DependencyStorageOverrideContext:
        """Context manager overriding dependency in with block"""
        implementation = implementation if implementation is not None else []
        implementations = implementation if isinstance(implementation, list) else [implementation]

        factory = factory if factory is not None else []
        factories = factory if isinstance(factory, list) else [factory]

        replaceable_implementations = self._dependencies.get(annotation, None)
        if replaceable_implementations is None:
            raise DependencyNotFound("Dependency not found in container")

        spoofed_implementations = []
        for implementation in implementations:
            spoofed_implementations.append(
                DependencyWrapper(type_=annotation, target=implementation, annotations=None, scope=Scope.SINGLETON)
            )

        for factory in factories:
            spoofed_implementations.append(_get_dependency_wrapper(annotation, factory, Scope.TRANSIENT))

        return DependencyStorageOverrideContext(
            self, annotation, spoofed_implementations, replaceable_implementations, is_clear_cache
        )

    def _override(
        self,
        annotation: Any,
        spoofed_implementations: List[Any],
        *,
        is_clear_cache: bool = True
    ) -> None:
        if is_clear_cache:
            self.clear_cache()
        self._dependencies[annotation] = spoofed_implementations

    def _release_overdetermined_dependency(self, annotation: Any, replaceable_implementations: List[Any]) -> None:
        self._dependencies[annotation] = replaceable_implementations

    def clear_cache(self) -> None:
        """clear the singleton dependency cache"""
        for dependency_wrappers in self._dependencies.values():
            for dependency_wrapper in dependency_wrappers:
                if dependency_wrapper.annotations is None and dependency_wrapper.cache is not None:
                    continue
                dependency_wrapper.cache = None

    def get_dependencies(self, *, ignore_annotation: Optional[Any] = None) -> Iterator[DependencyWrapper]:
        """Get unresolved iterator object/class"""
        for annotation, dependency_wrappers in self._dependencies.items():
            if annotation == ignore_annotation:
                continue
            for dependency_wrapper in dependency_wrappers:
                yield dependency_wrapper

    def get_dependencies_by_annotation(self, annotation: Any) -> List[DependencyWrapper]:
        """Get unresolved object/class by annotation"""
        return self._dependencies.get(annotation, [])

    def __len__(self) -> int:
        return len(self._dependencies)


class ConditionCollections(IConditionCollections):
    def __init__(
        self,
        resolver: IResolver,
        dependency_storage: DependencyStorage,
        conditions: Optional[List[Type[BaseCondition]]] = None,
        default_condition: Optional[Type[BaseCondition]] = None,
    ) -> None:
        self._resolver = resolver
        self._dependency_storage = dependency_storage

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
                return condition.handle(typing)

        if self._default_condition is not None:
            return self._default_condition.handle(typing)
        return None

    def _resolve_condition(self, condition: Type[BaseCondition]) -> BaseCondition:
        return condition(self._resolver, self._dependency_storage)

    def __iter__(self) -> Iterator[BaseCondition]:
        for condition in self._conditions:
            yield condition
        if self._default_condition is not None:
            yield self._default_condition

    def __len__(self) -> int:
        if self._default_condition is not None:
            return len(self._conditions) + 1
        return len(self._conditions)
