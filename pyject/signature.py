import inspect
from typing import Callable, Dict, Any, Optional
from typing import ForwardRef


def evaluate_forwardref(type_: ForwardRef, globalns: Any, localns: Any) -> Any:
    return type_._evaluate(globalns, localns)


def get_typed_signature(call: Callable) -> inspect.Signature:
    """Get the signatures of the callable object"""
    signature = inspect.signature(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=get_typed_annotation(param, globalns),
        )
        for param in signature.parameters.values()
    ]
    typed_signature = inspect.Signature(typed_params)
    return typed_signature


def get_typed_annotation(param: inspect.Parameter, globalns: Dict[str, Any]) -> Any:
    annotation = param.annotation
    if isinstance(annotation, str):
        try:
            annotation = ForwardRef(annotation)
            annotation = evaluate_forwardref(annotation, globalns, globalns)
        except (TypeError, NameError):
            annotation = param.annotation
    return annotation


def is_default_class(signature: inspect.Signature) -> bool:
    parameter: inspect.Parameter
    for index, (attr_name, parameter) in enumerate(signature.parameters.items()):
        if (
            (index == 0 and attr_name == "self" and parameter.annotation == parameter.empty)
            or (index == 1 and attr_name == "args" and parameter.annotation == parameter.empty)
            or (index == 2 and attr_name == "kwargs" and parameter.annotation == parameter.empty)
        ):
            continue
        else:
            return False
    return True


def get_signature_to_implementation(implementation: Any) -> Optional[inspect.Signature]:
    if inspect.isclass(implementation):
        signature = get_typed_signature(implementation.__init__)
        if is_default_class(signature):
            self_parameter = signature.parameters["self"]
            return inspect.Signature(
                [
                    inspect.Parameter(
                        name=self_parameter.name,
                        kind=self_parameter.kind,
                        default=self_parameter.default,
                        annotation=self_parameter.annotation,
                    )
                ]
            )
        return signature
    elif inspect.isfunction(implementation) or inspect.ismethod(implementation):
        return get_typed_signature(implementation)
    elif hasattr(implementation, "__call__"):
        return get_typed_signature(implementation.__call__)
    return None
