import inspect
import sys
from typing import Any, TypeVar, Type, Iterable, Union, Callable, Awaitable
import contextvars

T = TypeVar("T", bound="ContextInstanceMixin")


if sys.version_info >= (3, 9):
    from typing import get_origin

    collection_classes = [list, tuple, set, frozenset]
    _collection_typing_name = "Sequence"

    def check_collection_typing(annotation: Any) -> bool:
        origin = get_origin(annotation)
        if origin in collection_classes:
            return True

        annotation_type_name = getattr(annotation, "_name", None)
        if annotation_type_name is None:
            return False

        if annotation_type_name is not None and annotation_type_name == _collection_typing_name:
            return True
        return False
else:
    _collection_typing_name = {"Set", "List", "Tuple", "FrozenSet", "Sequence"}


    def check_collection_typing(annotation: Any) -> bool:
        annotation_type_name = getattr(annotation, "_name", None)
        if annotation_type_name is None:
            return False

        if annotation_type_name is not None and annotation_type_name in _collection_typing_name:
            return True
        return False


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


def check_generic_typing(annotation: Any, collection_type_names: Iterable[str]) -> bool:
    annotation_type_name = getattr(annotation, "_name", None)
    if annotation_type_name is not None and annotation_type_name in collection_type_names:
        return True
    return False


def is_coroutine_callable(call: Union[Callable[..., Any], Awaitable[Any]]) -> bool:
    if inspect.isroutine(call):
        return inspect.iscoroutinefunction(call)
    if inspect.isclass(call):
        return False
    call = getattr(call, "__call__", None)
    return inspect.iscoroutinefunction(call)


def check_union_typing(annotation: Any) -> bool:
    origin = getattr(annotation, "__origin__", None)
    if origin is not None and origin is Union:
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
