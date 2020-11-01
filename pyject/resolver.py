from typing import Dict, Any, TypeVar

from pyject.models import Scope, DependencyWrapper
from pyject.base import IResolver
from pyject.collections import DependencyStorage, ConditionCollections
from pyject.utils import _check_annotation

T = TypeVar("T")


class Resolver(IResolver):
    def __init__(
        self,
        dependency_storage: DependencyStorage,
    ) -> None:
        self._dependency_storage = dependency_storage
        self._condition_collections = ConditionCollections(self)

    def get_implementation_attr(self, annotations: Dict[str, Any]) -> Dict[str, Any]:
        """Get resolved signature attributes"""
        callable_object_arguments = {}
        for name, annotation in annotations.items():
            if name == "self":
                continue

            callable_object_arguments[name] = self._condition_collections.find(annotation)

        return callable_object_arguments

    def _get_implementation(self, dependency_wrapper: DependencyWrapper):
        if dependency_wrapper.annotations is None:
            return dependency_wrapper.target

        attr = self.get_implementation_attr(dependency_wrapper.annotations)
        return dependency_wrapper.target(**attr)

    def get_resolved_dependencies(self, typing: Any):
        wrappers = self._dependency_storage.get_dependencies_by_annotation(typing)
        for wrapper in wrappers:
            yield self._check_and_get_implementation(wrapper)

        for dependency_wrapper in self._dependency_storage.get_dependencies(ignore_annotation=typing):
            if not _check_annotation(typing, dependency_wrapper.type_):
                continue
            yield self._check_and_get_implementation(dependency_wrapper)

    def _check_and_get_implementation(self, dependency_wrapper: DependencyWrapper):
        if dependency_wrapper.scope == Scope.TRANSIENT:
            return self._get_implementation(dependency_wrapper)
        else:
            return dependency_wrapper.target
