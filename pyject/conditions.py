from typing import List, Any, Optional, Dict, Iterator, Sequence

from pyject.base import BaseCondition
from pyject.exception import DependencyResolvingException
from pyject.utils import check_generic_typing

# todo: Added: Optional, Union, Any


class DefaultCondition(BaseCondition):
    def get_attributes(self, typing: Any) -> Optional[Dict[str, Any]]:
        for dependency in self._dependency_storage.get_raw_dependency(typing):
            return self._resolver.get_implementation(dependency.target)
        raise DependencyResolvingException()


class CollectionCondition(BaseCondition):
    _collection_type_names = {"Set", "List", "Tuple", "FrozenSet", "Sequence"}

    def get_attributes(self, typing: Any) -> Optional[List[Dict[str, Any]]]:
        if not check_generic_typing(typing, self._collection_type_names):
            return None

        field_attributes = []
        for inner_type in typing.__args__:
            for dependency in self._dependency_storage.get_raw_dependency(inner_type):
                field_attributes.append(self._resolver.get_implementation(dependency.target))
        if not field_attributes:
            raise DependencyResolvingException()
        return field_attributes


class IteratorCondition(BaseCondition):
    _collection_type_names = {"Iterator"}

    def get_attributes(self, typing: Any) -> Optional[Iterator[Any]]:
        if not check_generic_typing(typing, self._collection_type_names):
            return None

        return self._iterator(typing.__args__)

    def _iterator(self, typings: Sequence[Any]):
        for typing in typings:
            for dependency in self._dependency_storage.get_raw_dependency(typing):
                yield self._resolver.get_implementation(dependency.target)
