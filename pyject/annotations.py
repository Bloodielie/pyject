import inspect
from typing import Any, get_type_hints, Dict, Optional


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


def get_annotations_to_implementation(implementation: Any) -> Optional[Dict[str, Any]]:
    if inspect.isclass(implementation):
        return get_annotations(implementation.__init__)
    elif inspect.isfunction(implementation) or inspect.ismethod(implementation):
        return get_annotations(implementation)
    elif hasattr(implementation, "__call__"):
        return get_annotations(implementation.__call__)
    return None
