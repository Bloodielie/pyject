from typing import Any, TypeVar, Type, List
import contextvars

T = TypeVar("T")


def _check_annotation(annotation: Any, dependency: Any) -> bool:
    try:
        if issubclass(annotation, dependency):
            return True
    except TypeError:
        try:
            if isinstance(annotation, dependency):
                return True
        except TypeError:
            if annotation == dependency:
                return True
    return False


def check_generic_typing(annotation: Any, collection_type_names: List[Any]) -> bool:
    annotation_type_name = getattr(annotation, "_name", None)
    if annotation_type_name is not None:
        for collection_type_name in collection_type_names:
            if annotation_type_name == collection_type_name:
                return True
    return False


class ContextInstanceMixin:
    def __init_subclass__(cls, **kwargs):
        cls.__context_instance = contextvars.ContextVar(f"instance_{cls.__name__}")
        return cls

    @classmethod
    def get_current(cls: Type[T], no_error=True) -> T:
        if no_error:
            return cls.__context_instance.get(None)
        return cls.__context_instance.get()

    @classmethod
    def set_current(cls: Type[T], value: T):
        if not isinstance(value, cls):
            raise TypeError(f"Value should be instance of {cls.__name__!r} not {type(value).__name__!r}")
        cls.__context_instance.set(value)
