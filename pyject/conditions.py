from typing import List, Any, Optional, Dict, Iterator, Sequence, NoReturn

from pyject.base import BaseCondition
from pyject.exception import DependencyResolvingException, TypingDoesNotMatch
from pyject.utils import check_generic_typing, check_union_typing


# todo: Added: Optional, Union


class DefaultCondition(BaseCondition):
    def get_attributes(self, typing: Any) -> Dict[str, Any]:
        for dependency in self._dependency_storage.get_raw_dependency(typing):
            return self._resolver.get_implementation(dependency.target)

        raise DependencyResolvingException(f"There is no such dependency in the container {typing}")


class AnyCondition(BaseCondition):
    _type_names_to_check = {"Any"}

    def get_attributes(self, typing: Any) -> NoReturn:
        if not check_generic_typing(typing, self._type_names_to_check):
            raise TypingDoesNotMatch()

        raise DependencyResolvingException(f"Any or empty annotation is not supported")


class UnionCondition(BaseCondition):
    def get_attributes(self, typing: Any) -> Optional[Dict[str, Any]]:
        if not check_union_typing(typing):
            raise TypingDoesNotMatch()
        args = typing.__args__

        if len(args) == 2 and args[1] is type(None):
            for dependency in self._dependency_storage.get_raw_dependency(args[0]):
                return self._resolver.get_implementation(dependency.target)
            return None

        for inner_type in args:
            for dependency in self._dependency_storage.get_raw_dependency(inner_type):
                return self._resolver.get_implementation(dependency.target)

        raise DependencyResolvingException(f"There is no such dependency in the container {typing}")


class CollectionCondition(BaseCondition):
    _type_names_to_check = {"Set", "List", "Tuple", "FrozenSet", "Sequence"}

    def get_attributes(self, typing: Any) -> List[Dict[str, Any]]:
        if not check_generic_typing(typing, self._type_names_to_check):
            raise TypingDoesNotMatch()

        field_attributes = []
        for inner_type in typing.__args__:
            for dependency in self._dependency_storage.get_raw_dependency(inner_type):
                field_attributes.append(self._resolver.get_implementation(dependency.target))
        if not field_attributes:
            raise DependencyResolvingException(f"There is no such dependency in the container {typing}")
        return field_attributes


class IteratorCondition(BaseCondition):
    _type_names_to_check = {"Iterator"}

    def get_attributes(self, typing: Any) -> Iterator[Any]:
        if not check_generic_typing(typing, self._type_names_to_check):
            raise TypingDoesNotMatch()

        return self._iterator(typing.__args__)

    def _iterator(self, typings: Sequence[Any]):
        for typing in typings:
            for dependency in self._dependency_storage.get_raw_dependency(typing):
                yield self._resolver.get_implementation(dependency.target)
