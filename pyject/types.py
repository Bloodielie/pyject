from typing import Generic, TypeVar, Type, Union, Optional, Any

from pyject.base import IResolver
from pyject.collections import DependencyStorage

T = TypeVar("T")


class ForwardRef(Generic[T]):
    def __init__(self, resolver: IResolver, dependency_storage: DependencyStorage) -> None:
        self.__resolver = resolver
        self.__dependency_storage = dependency_storage
        self.__instance: Optional[T] = None
        self.__generic_typing: Optional[Type[T]] = None
        self.__repr_str = f"<class '{self.__module__}.ForwardRef'>"

    def __set_generic_typing(self, generic_typing: Type[T]) -> None:
        self.__generic_typing = generic_typing
        self.__set_metadata(generic_typing)

    def __set_instance(self, instance: T) -> None:
        self.__set_metadata(instance)
        self.__instance = instance

    def __set_metadata(self, instance: Union[T, Type[T]]) -> None:
        self.__repr_str = str(instance)
        self.__module__ = getattr(instance, '__module__')
        self.__doc__ = getattr(instance, '__doc__')
        name = getattr(instance, '__name__', None)
        if name is not None:
            self.__name__ = name
        qualname = getattr(instance, '__qualname__', None)
        if qualname is not None:
            self.__qualname__ = qualname
        self.__annotations__ = getattr(instance, '__annotations__', {})

    def __repr__(self) -> str:
        return self.__repr_str

    def __getattr__(self, item: str) -> Any:
        if self.__instance is None:
            for instance in self.__resolver.get_forwardref_resolved_dependencies(self.__generic_typing):
                self.__set_instance(instance)
                break
            if self.__instance is None:
                for instance in self.__resolver.get_resolved_dependencies(self.__generic_typing):
                    self.__set_instance(instance)
                    break
                self.__dependency_storage.add_forwardref(self.__instance)
        return getattr(self.__instance, item)
