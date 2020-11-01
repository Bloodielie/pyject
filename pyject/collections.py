from contextvars import ContextVar
from typing import List, Optional, Any, Union, Type, Dict

from pyject.annotations import get_annotations_to_implementation
from pyject.models import Scope
from pyject.base import BaseCondition, IResolver, IConditionCollections
from pyject.conditions import DefaultCondition, AnyCondition, CollectionCondition, UnionCondition, IteratorCondition
from pyject.models import DependencyWrapper


class DependencyStorage:
    def __init__(self):
        self._dependencies: Dict[Any, List[DependencyWrapper]] = {}
        self._context_dependencies: ContextVar[Optional[List[DependencyWrapper]]] = ContextVar(f"_context_storage_{id(self)}")

    def add(self, annotation: Any, implementation: Any, scope: Union[Scope, int]) -> None:
        wrapper = DependencyWrapper(
            type_=annotation, target=implementation, annotations=get_annotations_to_implementation(implementation), scope=scope
        )
        dependency = self._dependencies.get(annotation, None)
        if dependency is None:
            self._dependencies[annotation] = [wrapper]
        else:
            dependency.append(wrapper)

    def add_context(self, annotation: Any, implementation: Any, scope: Union[Scope, int]) -> None:
        wrapper = DependencyWrapper(
            type_=annotation, target=implementation, annotations=get_annotations_to_implementation(implementation), scope=scope
        )
        new_context_dependencies = [wrapper]

        context_dependencies = self._context_dependencies.get(None)
        if context_dependencies is None:
            self._context_dependencies.set(new_context_dependencies)
        else:
            new_context_dependencies.extend(context_dependencies)
            self._context_dependencies.set(new_context_dependencies)

    def get_dependencies(self, *, ignore_annotation: Optional[Any] = None):
        """Get unresolved object/class"""
        for dependency_wrapper in self._context_dependencies.get([]):  # type: ignore
            yield dependency_wrapper

        for dependency_wrappers in self._dependencies.values():
            for dependency_wrapper in dependency_wrappers:
                if dependency_wrapper.type_ == ignore_annotation:
                    continue
                yield dependency_wrapper

    def get_dependencies_by_annotation(self, annotation: Any) -> List[DependencyWrapper]:
        return self._dependencies.get(annotation, [])

    def __len__(self) -> int:
        return len(self._dependencies) + len(self._context_dependencies.get([]))  # type: ignore


class ConditionCollections(IConditionCollections):
    def __init__(
        self,
        resolver: IResolver,
        conditions: Optional[List[Type[BaseCondition]]] = None,
    ) -> None:
        self._resolver = resolver

        self._conditions = []
        if conditions is not None:
            for condition in conditions:
                self._conditions.append(self._resolve_condition(condition))

        self._setup_base_conditions()

    def add_condition(self, condition: Type[BaseCondition]) -> None:
        self._conditions.append(self._resolve_condition(condition))

    def find(self, typing: Any) -> Optional[Any]:
        for condition in self._conditions:
            if condition.check_typing(typing):
                return condition.get_attributes(typing)

        return self._default_condition.get_attributes(typing)

    def _setup_base_conditions(self) -> None:
        self._default_condition = self._resolve_condition(DefaultCondition)
        self.add_condition(AnyCondition)
        self.add_condition(CollectionCondition)
        self.add_condition(UnionCondition)
        self.add_condition(IteratorCondition)

    def _resolve_condition(self, condition: Type[BaseCondition]) -> BaseCondition:
        return condition(self._resolver)
