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
def filled_resolver(dependency_storage):
    dependency_storage.add(QuackBehavior, Sqeak, Scope.TRANSIENT)
    dependency_storage.add(DuckInterface, DuckA, Scope.TRANSIENT)
    dependency_storage.add(DuckInterface, DuckB, Scope.TRANSIENT)
    dependency_storage.add(DuckInterface, DuckC, Scope.TRANSIENT)
    return Resolver(dependency_storage)


def test_get_resolved_dependencies(filled_resolver):
    for duck in filled_resolver.get_resolved_dependencies(DuckInterface):
        assert isinstance(duck, DuckInterface)

    for sqeak in filled_resolver.get_resolved_dependencies(QuackBehavior):
        assert isinstance(sqeak, QuackBehavior)


def test_get_implementation_attr(filled_resolver):
    attrs = filled_resolver.get_implementation_attr({"squeak": QuackBehavior, "self": typing.Any})
    assert isinstance(attrs, dict) is True
    for key, value in attrs.items():
        assert isinstance(key, str) is True
        assert key == "squeak"
        assert isinstance(value, QuackBehavior) is True

    attrs = filled_resolver.get_implementation_attr({})
    assert isinstance(attrs, dict) is True
