from typing import List, Any, Optional, Dict

from pyject.base import BaseCondition
from pyject.utils import check_generic_typing


class DefaultCondition(BaseCondition):
    def get_attributes(self, typing: Any) -> Optional[List[Dict[str, Any]]]:
        for dependency in self._dependency_storage.get_raw_dependency(typing):
            return self._resolver.get_implementation(dependency.target)
        return None


class CollectionCondition(BaseCondition):
    _collection_type_names = ["Set", "List", "Tuple", "FrozenSet"]

    def get_attributes(self, typing: Any) -> Optional[List[Dict[str, Any]]]:
        if not check_generic_typing(typing, self._collection_type_names):
            return None

        field_attributes = []
        (inner_type,) = typing.__args__
        for dependency in self._dependency_storage.get_raw_dependency(inner_type):
            field_attributes.append(self._resolver.get_implementation(dependency.target))
        return field_attributes
