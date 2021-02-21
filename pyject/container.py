import sys
from typing import Any, List, TypeVar, Type, Optional, Dict, Union, Callable, Awaitable, overload, Iterator

from pyject.base import IContainer
from pyject.exception import DependencyNotFound, DependencyResolvingException
from pyject.models import Scope
from pyject.collections import DependencyStorage, DependencyStorageOverrideContext
from pyject.resolver import Resolver
from pyject.annotations import get_annotations_to_implementation
from pyject.utils import ContextInstanceMixin, is_coroutine_callable

if sys.version_info == (3, 7):
    from typing_extensions import get_args
else:
    from typing import get_args

T = TypeVar("T")


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

    def add_context(self, annotation: Any, implementation: Any) -> None:
        """Add a class/object that can only be retrieved in the same context"""
        self._dependency_storage.add(annotation, implementation, Scope.CONTEXT)

    @overload
    def get(self, annotation: Type[T]) -> T:
        ...

    @overload
    def get(self, annotation: Any) -> Any:
        ...

    def get(self, annotation):
        """Get object from container"""
        type_args = get_args(annotation)
        if type_args:
            annotation = (annotation, type_args)

        for dependency in self._resolver.get_resolved_dependencies(annotation):
            return dependency

        raise DependencyNotFound("Dependency not found")

    @overload
    def get_all(self, annotation: Type[T]) -> T:
        ...

    @overload
    def get_all(self, annotation: Any) -> Any:
        ...

    def get_all(self, annotation):
        """Get all object from container"""
        type_args = get_args(annotation)
        if type_args:
            annotation = (annotation, type_args)

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

    def override(
        self,
        annotation: Any,
        implementation: Optional[Union[List[Any], Any]] = None,
        factory: Optional[Union[List[Any], Any]] = None,
        *,
        is_clear_cache: bool = True
    ) -> DependencyStorageOverrideContext:
        """Context manager overriding dependency in with block"""
        return self._dependency_storage.override(annotation, implementation, factory, is_clear_cache=is_clear_cache)  # type: ignore

    def __len__(self) -> int:
        return len(self._dependency_storage)
