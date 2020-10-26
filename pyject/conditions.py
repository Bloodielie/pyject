from typing import List, Any, Optional, Dict, Iterator

from pyject.base import BaseCondition
from pyject.models import DependencyWrapper
from pyject.utils import check_generic_typing

# todo: Added: Optional, Union


class DefaultCondition(BaseCondition):
    def get_attributes(self, typing: Any) -> Optional[Dict[str, Any]]:
        for dependency in self._dependency_storage.get_raw_dependency(typing):
            return self._resolver.get_implementation(dependency.target)
        return None


class CollectionCondition(BaseCondition):
    _collection_type_names = ["Set", "List", "Tuple", "FrozenSet", "Sequence"]

    def get_attributes(self, typing: Any) -> Optional[List[Dict[str, Any]]]:
        if not check_generic_typing(typing, self._collection_type_names):
            return None

        field_attributes = []
        (inner_type,) = typing.__args__
        for dependency in self._dependency_storage.get_raw_dependency(inner_type):
            field_attributes.append(self._resolver.get_implementation(dependency.target))
        return field_attributes


class IteratorCondition(BaseCondition):
    _collection_type_names = ["Iterator"]

    def get_attributes(self, typing: Any) -> Optional[Iterator[Any]]:
        if not check_generic_typing(typing, self._collection_type_names):
            return None

        (inner_type,) = typing.__args__
        return self._iterator(
            self._dependency_storage.get_raw_dependency(inner_type), self._resolver.get_implementation
        )

    @staticmethod
    def _iterator(iterator_for_get_raw_dependencies: Iterator[DependencyWrapper], func_for_resolving_implementation):
        for dependency in iterator_for_get_raw_dependencies:
            yield func_for_resolving_implementation(dependency.target)
