from typing import List, Any, Optional, Dict

from pyject.base import BaseCondition


class DefaultCondition(BaseCondition):
    def get_attributes(self, typing: Any) -> Optional[List[Dict[str, Any]]]:
        for dependency in self._dependency_storage.get_raw_dependency(typing):
            return self._resolver.get_implementation(dependency.target)
        return None


class CollectionCondition(BaseCondition):
    _collection_type_names = ["Set", "List", "Tuple", "FrozenSet"]

    def get_attributes(self, typing: Any) -> Optional[List[Dict[str, Any]]]:
        if not self._is_collection_type(typing):
            return None
        field_attributes = []
        (inner_type,) = typing.__args__
        for dependency in self._dependency_storage.get_raw_dependency(inner_type):
            field_attributes.append(self._resolver.get_implementation(dependency.target))
        return field_attributes

    def _is_collection_type(self, annotation: Any) -> bool:
        annotation_type_name = getattr(annotation, "_name", None)
        if annotation_type_name is not None:
            for collection_type_name in self._collection_type_names:
                if annotation_type_name == collection_type_name:
                    return True
        return False
