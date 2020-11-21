import inspect
from typing import Any, get_type_hints, Dict, Optional, Tuple


def get_annotations(implementation: Any) -> Dict[str, Any]:
    type_hints = get_type_hints(implementation)
    if "return" in type_hints:
        del type_hints["return"]

    implementation_code = getattr(implementation, "__code__", None)
    if implementation_code is None:
        return type_hints

    for argument in implementation.__code__.co_varnames:
        if argument in type_hints:
            continue
        type_hints[argument] = Any

    return type_hints


def convert_dict_annotation_to_tuple(dict_: Dict[str, Any]) -> Tuple[Tuple[str, Any]]:
    return tuple(((name, annotation) for name, annotation in dict_.items()))


def get_annotations_to_implementation(implementation: Any) -> Optional[Tuple[Tuple[str, Any]]]:
    if inspect.isclass(implementation):
        annotations = get_annotations(implementation.__init__)
    elif inspect.isfunction(implementation) or inspect.ismethod(implementation):
        annotations = get_annotations(implementation)
    elif hasattr(implementation, "__call__"):
        annotations = get_annotations(implementation.__call__)
    else:
        return None
    return convert_dict_annotation_to_tuple(annotations)
