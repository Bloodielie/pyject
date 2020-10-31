from typing import Any, List, TypeVar, Type, Optional, Dict, Union

from pyject.base import IContainer
from pyject.exception import DependencyNotFound
from pyject.models import Scope
from pyject.collections import DependencyStorage
from pyject.resolver import Resolver
from pyject.signature import get_signature_to_implementation
from pyject.utils import ContextInstanceMixin

T = TypeVar("T")


# todo: сделать оптимизацию, сначало искать в dict а потом пробигаться по нему


class Container(IContainer, ContextInstanceMixin):
    def __init__(self) -> None:
        self._dependency_storage = DependencyStorage()

        self._resolver = Resolver(self._dependency_storage)

        self.add_constant(Container, self)
        self.set_current(self)

    def add_singleton(self, annotation: Any, implementation: Any) -> None:
        """Add a class that will be initialized once when added"""
        implementation = self._resolver.get_implementation(implementation)
        self._dependency_storage.add(annotation, implementation, Scope.SINGLETON)

    def add_constant(self, annotation: Any, implementation: Any) -> None:
        """Adds an object that does not need to be initialized"""
        self._dependency_storage.add(annotation, implementation, Scope.SINGLETON)

    def add_transient(self, annotation: Any, implementation: Any) -> None:
        """Add a class that will be initialized with each request"""
        self._dependency_storage.add(annotation, implementation, Scope.TRANSIENT)

    def add_context(self, annotation: Any, implementation: Any, *, scope: Union[Scope, int] = Scope.TRANSIENT) -> None:
        """Add a class/object that can only be retrieved in the same context"""
        self._dependency_storage.add(annotation, implementation, scope, in_context=True)

    def get(self, annotation: Type[T]) -> T:
        """Get object from container"""
        for dependency in self._resolver.get_resolved_dependencies(annotation):
            return dependency

        raise DependencyNotFound("Dependency not found")

    def get_all(self, annotation: Type[T]) -> List[T]:
        """Get all object from container"""
        dependencies = []
        for dependency in self._resolver.get_resolved_dependencies(annotation):
            dependencies.append(dependency)
        return dependencies

    def get_target_attributes(self, target: Any) -> Optional[Dict[str, Any]]:
        """Get resolved object attributes"""
        signature = get_signature_to_implementation(target)
        if signature is not None:
            return self._resolver.get_implementation_attr(signature)
        return None

    def __len__(self) -> int:
        return len(self._dependency_storage)
