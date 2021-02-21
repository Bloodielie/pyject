from abc import ABC, abstractmethod
from typing import Type, TypeVar, List, Any, Dict, Optional, Union, Iterator, overload, Callable, Awaitable, Tuple

from pyject.models import Scope

T = TypeVar("T")


class IContainer(ABC):
    @abstractmethod
    def add_singleton(self, annotation: Type[T], implementation: T) -> None:
        """Add a class that will be initialized once when added"""

    @abstractmethod
    def add_constant(self, annotation: Type[T], implementation: T) -> None:
        """Adds an object that does not need to be initialized"""

    @abstractmethod
    def add_transient(self, annotation: Type[T], implementation: T) -> None:
        """Add a class that will be initialized with each request"""

    @abstractmethod
    def add_context(self, annotation: Type[T], implementation: T) -> None:
        """Add a class/object that can only be retrieved in the same context"""

    @abstractmethod
    def get(self, annotation: Type[T]) -> T:
        """Get object from container"""

    @abstractmethod
    def get_all(self, annotation: Type[T]) -> List[T]:
        """Get all object from container"""

    @abstractmethod
    def get_target_attributes(self, target: Any) -> Optional[Dict[str, Any]]:
        """Get resolved object attributes"""

    @overload
    def resolve(self, target: Type[T]) -> T:
        ...

    @overload
    def resolve(self, target: Callable[..., T]) -> T:
        ...

    @abstractmethod
    def resolve(self, target):
        ...

    @abstractmethod
    async def async_resolve(self, target: Callable[..., Awaitable[T]]) -> T:
        ...


class IResolver(ABC):
    @abstractmethod
    def get_implementation_attr(self, annotations: Tuple[Tuple[str, Any]]) -> Dict[str, Any]:
        """Get resolved signature attributes"""

    @abstractmethod
    def get_forwardref_resolved_dependencies(self, typing: Any) -> Iterator[Any]:
        """An iterator that returns resolved dependencies"""

    @abstractmethod
    def get_resolved_dependencies(self, typing: Any) -> Iterator[Any]:
        """An iterator that returns resolved dependencies"""


class BaseCondition(ABC):
    def __init__(self, resolver: IResolver, dependency_storage):
        self._resolver = resolver
        self._dependency_storage = dependency_storage

    @abstractmethod
    def check_typing(self, typing: Any) -> bool:
        """Get attributes from container for typing"""

    @abstractmethod
    def handle(self, typing: Any) -> Any:
        """Get attributes from container for typing"""


class IConditionCollections(ABC):
    @abstractmethod
    def add(self, condition: Type["BaseCondition"]) -> None:
        """Add a condition to apply it in the dependency solution"""

    @abstractmethod
    def find(self, typing: Any) -> Optional[Any]:
        """Finding a condition for type and getting attributes"""
