from typing import Any, List, TypeVar, Type, Optional, Dict, Union, Callable, Awaitable, overload

from pyject.base import IContainer
from pyject.exception import DependencyNotFound, DependencyResolvingException
from pyject.models import Scope
from pyject.collections import DependencyStorage
from pyject.resolver import Resolver
from pyject.annotations import get_annotations_to_implementation
from pyject.utils import ContextInstanceMixin, is_coroutine_callable

T = TypeVar("T")


# todo: сделать поддержку asyncio


class Container(IContainer, ContextInstanceMixin):
    def __init__(self) -> None:
        self._dependency_storage = DependencyStorage()

        self._resolver = Resolver(self._dependency_storage)

        self.add_constant(Container, self)
        self.set_current(self)

    def add_singleton(self, annotation: Any, implementation: Any) -> None:
        """Add a class that will be initialized once when added"""
        self._dependency_storage.add(annotation, implementation, Scope.SINGLETON)

    def add_constant(self, annotation: Any, implementation: Any) -> None:
        """Adds an object that does not need to be initialized"""
        self._dependency_storage.add(annotation, implementation, Scope.SINGLETON)

    def add_transient(self, annotation: Any, implementation: Any) -> None:
        """Add a class that will be initialized with each request"""
        self._dependency_storage.add(annotation, implementation, Scope.TRANSIENT)

    def add_context(self, annotation: Any, implementation: Any, *, scope: Union[Scope, int] = Scope.TRANSIENT) -> None:
        """Add a class/object that can only be retrieved in the same context"""
        self._dependency_storage.add_context(annotation, implementation, scope)

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
        annotations = get_annotations_to_implementation(target)
        if annotations is not None:
            return self._resolver.get_implementation_attr(annotations)
        return None

    @overload
    def resolve(self, target: Type[T]) -> T:
        ...

    @overload
    def resolve(self, target: Callable[..., T]) -> T:
        ...

    def resolve(self, target):
        """Get resolved object"""
        attrs = self.get_target_attributes(target)
        if attrs is None:
            raise DependencyResolvingException("Failed to get target attributes")
        return target(**attrs)

    async def async_resolve(self, target: Callable[..., Awaitable[T]]) -> T:
        """Get resolved async object"""
        if is_coroutine_callable(target):
            attrs = self.get_target_attributes(target)
            if attrs is None:
                raise DependencyResolvingException("Failed to get target attributes")
            return await target(**attrs)
        raise DependencyResolvingException("Target is not an asynchronous function")

    def __len__(self) -> int:
        return len(self._dependency_storage)
