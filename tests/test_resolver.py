import typing
from pytest import fixture

from pyject import Scope
from pyject.collections import DependencyStorage
from pyject.resolver import Resolver
from tests.classes import QuackBehavior, Sqeak, DuckInterface, DuckA, DuckB, DuckC


@fixture()
def dependency_storage():
    return DependencyStorage()


@fixture()
def resolver(dependency_storage):
    dependency_storage.add_transient(QuackBehavior, Sqeak)
    dependency_storage.add_transient(DuckInterface, DuckA)
    dependency_storage.add_transient(DuckInterface, DuckB)
    dependency_storage.add_transient(DuckInterface, DuckC)
    return Resolver(dependency_storage)


def test_get_resolved_dependencies(resolver):
    for duck in resolver.get_resolved_dependencies(DuckInterface):
        assert isinstance(duck, DuckInterface)

    for sqeak in resolver.get_resolved_dependencies(QuackBehavior):
        assert isinstance(sqeak, QuackBehavior)


def test_get_implementation_attr(resolver):
    attrs = resolver.get_implementation_attr(tuple([("squeak", QuackBehavior), ("self", typing.Any)]))
    assert isinstance(attrs, dict) is True
    for key, value in attrs.items():
        assert isinstance(key, str) is True
        assert key == "squeak"
        assert isinstance(value, QuackBehavior) is True

    attrs = resolver.get_implementation_attr(tuple())
    assert isinstance(attrs, dict) is True
