import typing

from pyject.annotations import get_annotations_to_implementation, get_annotations


class BaseTestClass:
    def __init__(self):
        pass

    def test(self, a: str):
        pass

    def __call__(self, b: "str"):
        pass


def test_get_annotations():
    annotations = get_annotations(BaseTestClass.__init__)

    assert isinstance(annotations, dict)
    for key in annotations.keys():
        assert isinstance(key, str)

    assert annotations == {"self": typing.Any}

    instance = BaseTestClass()
    annotations = get_annotations(instance.test)
    assert annotations == {"self": typing.Any, "a": str}

    annotations = get_annotations(instance.__call__)
    assert annotations == {"self": typing.Any, "b": str}


def test_get_annotation_to_implementation():
    instance = BaseTestClass()

    method_annotations = get_annotations_to_implementation(instance.test)
    assert method_annotations == get_annotations(instance.test)
    class_annotations = get_annotations_to_implementation(BaseTestClass)
    assert class_annotations == get_annotations(BaseTestClass.__init__)
    class_call_annotations = get_annotations_to_implementation(instance)
    assert class_call_annotations == get_annotations(instance.__call__)

    for annotations in [method_annotations, class_annotations, class_call_annotations]:
        assert isinstance(annotations, dict)

        for key in annotations.keys():
            assert isinstance(key, str)
