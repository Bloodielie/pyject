import inspect
from typing import Dict, Any, List, TypeVar, Type, Iterator, overload, Optional

from pyject.base import BaseContainer
from pyject.exception import DependencyNotFound
from pyject.models import DependencyWrapper, Scope
from pyject.signature import get_typed_signature, get_signature_to_implementation
from pyject.utils import _check_annotation, _is_collection_type
from pyject.utils import ContextInstanceMixin
from contextvars import ContextVar

T = TypeVar("T")


class Container(BaseContainer, ContextInstanceMixin):
    def __init__(self) -> None:
        self._dependency_storage: List[DependencyWrapper] = []
        self._context_dependency_storage: ContextVar[Optional[List[DependencyWrapper]]] = ContextVar(
            f"_context_storage_{id(self)}"
        )

        self.add_constant(Container, self)
        self.set_current(self)

    def add_singleton(self, annotation: Any, implementation: Any) -> None:
        """Add a class that will be initialized once when added"""
        attr = self._get_implementation_attr(get_typed_signature(implementation))
        wrapper = DependencyWrapper(type_=annotation, target=implementation(**attr), scope=Scope.SINGLETON)
        self._dependency_storage.append(wrapper)

    def add_constant(self, annotation: Any, implementation: Any) -> None:
        """Adds an object that does not need to be initialized"""
        wrapper = DependencyWrapper(type_=annotation, target=implementation, scope=Scope.SINGLETON)
        self._dependency_storage.append(wrapper)

    def add_transient(self, annotation: Any, implementation: Any) -> None:
        """Add a class that will be initialized with each request"""
        wrapper = DependencyWrapper(type_=annotation, target=implementation, scope=Scope.TRANSIENT)
        self._dependency_storage.append(wrapper)

    def add_context(self, annotation: Any, implementation: Any) -> None:
        """Add a class/object that can only be retrieved in the same context"""
        wrapper = DependencyWrapper(type_=annotation, target=implementation, scope=Scope.TRANSIENT)

        context_dependency_storage = self._context_dependency_storage.get(None)
        if context_dependency_storage is None:
            self._context_dependency_storage.set([wrapper])
        else:
            context_dependency_storage.append(wrapper)

    def get(self, annotation: Type[T]) -> T:
        """Get object from container"""
        for dependency_wrapper in self._get_raw_dependency(annotation):
            if dependency_wrapper.scope == Scope.TRANSIENT:
                return self._get_implementation(dependency_wrapper.target)
            else:
                return dependency_wrapper.target
        raise DependencyNotFound("Dependency not found")

    def get_all(self, annotation: Type[T]) -> List[T]:
        """Get all object from container"""
        dependency_wrappers = []
        for dependency_wrapper in self._get_raw_dependency(annotation):
            if dependency_wrapper.scope == Scope.TRANSIENT:
                dependency_wrappers.append(self._get_implementation(dependency_wrapper.target))
            else:
                dependency_wrappers.append(dependency_wrapper.target)
        return dependency_wrappers

    def _get_implementation_attr(self, signature: inspect.Signature) -> Dict[str, Any]:
        """Get resolved signature attributes"""
        callable_object_arguments = {}
        for attr_name, parameter in signature.parameters.items():
            if attr_name == "self":
                continue

            annotation = parameter.annotation
            if _is_collection_type(annotation):
                field_attributes = []
                (inner_type,) = annotation.__args__
                for dependency in self._get_raw_dependency(inner_type):
                    field_attributes.append(self._get_implementation(dependency.target))
                callable_object_arguments[attr_name] = field_attributes
            else:
                for dependency in self._get_raw_dependency(annotation):
                    callable_object_arguments[attr_name] = self._get_implementation(dependency.target)

        return callable_object_arguments

    @overload
    def _get_implementation(self, implementation: Type[T]) -> T:
        ...

    @overload
    def _get_implementation(self, implementation: T) -> T:
        ...

    def _get_implementation(self, implementation):
        signature = get_signature_to_implementation(implementation)
        if signature is not None:
            attr = self._get_implementation_attr(signature)
            implementation = implementation(**attr)
        return implementation

    def get_target_attributes(self, target: Any) -> Dict[str, Any]:
        """Get resolved object attributes"""
        return self._get_implementation_attr(get_typed_signature(target))

    def _get_raw_dependency(self, annotation: Any) -> Iterator[DependencyWrapper]:
        """Get unresolved object/class"""
        context_dependency_storage = self._context_dependency_storage.get(None)
        if context_dependency_storage is None:
            storages = [self._dependency_storage]
        else:
            storages = [context_dependency_storage, self._dependency_storage]

        for dependency_wrapper in self._get_checked_dependency_in_storages(annotation, storages):
            yield dependency_wrapper

    @staticmethod
    def _get_checked_dependency_in_storages(
        annotation: Any, storages: List[List[DependencyWrapper]]
    ) -> Iterator[DependencyWrapper]:
        for storage in storages:
            for dependency_wrapper in storage:
                if _check_annotation(annotation, dependency_wrapper.type_):
                    yield dependency_wrapper

    def __len__(self) -> int:
        return len(self._dependency_storage) + len(self._context_dependency_storage.get([]))
