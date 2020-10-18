import inspect

from pyject.signature import get_signature_to_implementation, get_typed_signature


class BaseTestClass:
    def __init__(self):
        pass

    def test(self):
        pass

    def __call__(self):
        pass


def test_get_typed_signature():
    signature = get_typed_signature(BaseTestClass)
    assert signature == inspect.signature(BaseTestClass)


def test_get_signature_to_implementation():
    class_signature = get_signature_to_implementation(BaseTestClass)
    assert class_signature == inspect.signature(BaseTestClass.__init__)

    instance = BaseTestClass()

    method_signature = get_signature_to_implementation(instance.test)
    assert method_signature == inspect.signature(instance.test)

    class_call_signature = get_signature_to_implementation(instance)
    assert class_call_signature == inspect.signature(instance.__call__)
