import inspect
from typing import Dict, Any, TypeVar

from pyject.models import Scope
from pyject.base import IResolver
from pyject.collections import DependencyStorage, ConditionCollections
from pyject.signature import get_signature_to_implementation

T = TypeVar("T")


class Resolver(IResolver):
    def __init__(
        self,
        dependency_storage: DependencyStorage,
    ) -> None:
        self._dependency_storage = dependency_storage
        self._condition_collections = ConditionCollections(self)

    def get_implementation_attr(self, signature: inspect.Signature) -> Dict[str, Any]:
        """Get resolved signature attributes"""
        callable_object_arguments = {}
        for index, (attr_name, parameter) in enumerate(signature.parameters.items()):
            if attr_name == "self" and index == 0:
                continue

            annotation = parameter.annotation
            if parameter.empty == annotation:
                annotation = Any

            callable_object_arguments[attr_name] = self._condition_collections.find(annotation)

        return callable_object_arguments

    def get_implementation(self, implementation):
        """Check and get resolved implementation"""
        signature = get_signature_to_implementation(implementation)
        if signature is not None:
            attr = self.get_implementation_attr(signature)
            implementation = implementation(**attr)
        return implementation

    def get_resolved_dependencies(self, typing: Any):
        for dependency_wrapper in self._dependency_storage.get_raw_dependency(typing):
            if dependency_wrapper.scope == Scope.TRANSIENT:
                yield self.get_implementation(dependency_wrapper.target)
            else:
                yield dependency_wrapper.target
