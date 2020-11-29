from typing import List, Any, Optional, Dict, Iterator, Sequence, NoReturn

from pyject.base import BaseCondition
from pyject.exception import DependencyResolvingException
from pyject.types import ForwardRef
from pyject.utils import check_generic_typing, check_union_typing


class DefaultCondition(BaseCondition):
    def check_typing(self, typing: Any) -> bool:
        return True

    def get_attributes(self, typing: Any) -> Dict[str, Any]:
        for dependency in self._resolver.get_resolved_dependencies(typing):
            return dependency

        raise DependencyResolvingException(f"There is no such dependency in the container {typing}")


class AnyCondition(BaseCondition):
    _type_names_to_check = {"Any"}

    def check_typing(self, typing: Any) -> bool:
        if not check_generic_typing(typing, self._type_names_to_check):
            return False
        return True

    def get_attributes(self, typing: Any) -> NoReturn:
        raise DependencyResolvingException(f"Any or empty annotation is not supported")


class UnionCondition(BaseCondition):
    def check_typing(self, typing: Any) -> bool:
        if not check_union_typing(typing):
            return False
        return True

    def get_attributes(self, typing: Any) -> Optional[Dict[str, Any]]:
        args = typing.__args__

        if len(args) == 2 and args[1] is type(None):
            for dependency in self._resolver.get_resolved_dependencies(args[0]):
                return dependency
            return None

        for inner_type in args:
            for dependency in self._resolver.get_resolved_dependencies(inner_type):
                return dependency

        raise DependencyResolvingException(f"There is no such dependency in the container {typing}")


class CollectionCondition(BaseCondition):
    _type_names_to_check = {"Set", "List", "Tuple", "FrozenSet", "Sequence"}

    def check_typing(self, typing: Any) -> bool:
        if not check_generic_typing(typing, self._type_names_to_check):
            return False
        return True

    def get_attributes(self, typing: Any) -> List[Dict[str, Any]]:
        field_attributes = []
        for inner_type in typing.__args__:
            for dependency in self._resolver.get_resolved_dependencies(inner_type):
                field_attributes.append(dependency)

        if not field_attributes:
            raise DependencyResolvingException(f"There is no such dependency in the container {typing}")
        return field_attributes


class IteratorCondition(BaseCondition):
    _type_names_to_check = {"Iterator"}

    def check_typing(self, typing: Any) -> bool:
        if not check_generic_typing(typing, self._type_names_to_check):
            return False
        return True

    def get_attributes(self, typing: Any) -> Iterator[Any]:
        return self._iterator(typing.__args__)

    def _iterator(self, typings: Sequence[Any]):
        for typing in typings:
            for dependency in self._resolver.get_resolved_dependencies(typing):
                yield dependency


class ForwardRefCondition(BaseCondition):
    _type_names_to_check = {"ForwardRef"}

    def check_typing(self, typing: Any) -> bool:
        origin = getattr(typing, "__origin__", None)
        if origin is None:
            return False
        if issubclass(origin, ForwardRef):
            return True
        return False

    def get_attributes(self, typing: Any) -> ForwardRef:
        forward_ref = typing(self._resolver, self._dependency_storage)
        forward_ref._ForwardRef__set_generic_typing(forward_ref.__orig_class__.__args__[0])
        return forward_ref
