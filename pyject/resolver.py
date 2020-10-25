import inspect
from typing import Dict, Any, TypeVar, Optional, List, Type

from pyject.base import IResolver, BaseCondition
from pyject.conditions import CollectionCondition, DefaultCondition
from pyject.models import DependencyStorage
from pyject.signature import get_signature_to_implementation

T = TypeVar("T")


class Resolver(IResolver):
    def __init__(
        self,
        dependency_storage: DependencyStorage,
        conditions: Optional[List[Type[BaseCondition]]] = None,
    ) -> None:
        self._dependency_storage = dependency_storage

        self._conditions = []
        if conditions is not None:
            for condition in conditions:
                self._conditions.append(self._resolve_condition(condition))

        self._default_condition = DefaultCondition(self._dependency_storage, self)
        self._setup_base_conditions()

    def get_implementation_attr(self, signature: inspect.Signature) -> Dict[str, Any]:
        """Get resolved signature attributes"""
        callable_object_arguments = {}
        for attr_name, parameter in signature.parameters.items():
            if attr_name == "self":
                continue

            attrs = self._find(parameter.annotation)
            if attrs is None:
                continue
            callable_object_arguments[attr_name] = attrs

        return callable_object_arguments

    def get_implementation(self, implementation):
        """Check and get resolved implementation"""
        signature = get_signature_to_implementation(implementation)
        if signature is not None:
            attr = self.get_implementation_attr(signature)
            implementation = implementation(**attr)
        return implementation

    def add_condition(self, condition: Type[BaseCondition]) -> None:
        self._conditions.append(self._resolve_condition(condition))

    def _find(self, typing: Any) -> Optional[Any]:
        for condition in self._conditions:
            attrs = condition.get_attributes(typing)
            if attrs is None:
                continue
            return attrs

        return self._default_condition.get_attributes(typing)

    def _setup_base_conditions(self) -> None:
        self.add_condition(CollectionCondition)

    def _resolve_condition(self, condition: Type[BaseCondition]) -> BaseCondition:
        return condition(self._dependency_storage, self)