from abc import ABC, abstractmethod
from inspect import Signature
from typing import Type, TypeVar, List, Any, Dict, overload, Optional, Union

from pyject.models import DependencyStorage, Scope

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
    def add_context(self, annotation: Type[T], implementation: T, *, scope: Union[Scope, int] = Scope.TRANSIENT) -> None:
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


class IResolver(ABC):
    @overload
    def get_implementation(self, implementation: Type[T]) -> T:
        ...

    @overload
    def get_implementation(self, implementation: T) -> T:
        ...

    @abstractmethod
    def get_implementation(self, implementation):
        """Check and get resolved implementation"""

    @abstractmethod
    def get_implementation_attr(self, signature: Signature) -> Dict[str, Any]:
        """Get resolved signature attributes"""

    @abstractmethod
    def add_condition(self, condition: Type["BaseCondition"]) -> None:
        """Add a condition to apply it in the dependency solution"""


class BaseCondition(ABC):
    def __init__(self, dependency_storage: DependencyStorage, resolver: IResolver):
        self._dependency_storage = dependency_storage
        self._resolver = resolver

    @abstractmethod
    def get_attributes(self, typing: Any) -> Optional[Any]:
        """Get attributes from container for typing"""
