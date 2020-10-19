from abc import ABC, abstractmethod
from typing import Type, TypeVar, List, Any, Dict

T = TypeVar("T")


class BaseContainer(ABC):
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
    def get_target_attributes(self, target: Any) -> Dict[str, Any]:
        """Get resolved object attributes"""
