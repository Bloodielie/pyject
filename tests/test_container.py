from typing import List, Iterator

import pytest

from pyject.exception import DependencyNotFound, DependencyResolvingException

from pytest import fixture, raises

from pyject.container import Container
from tests.classes import QuackBehavior, Sqeak, DuckInterface, DuckA, DuckB, DuckC, duck_d
from contextvars import copy_context
from unittest import mock


@fixture()
def container():
    return Container()


@fixture()
def container_with_transient_classes(container):
    container.add_transient(QuackBehavior, Sqeak)
    container.add_transient(DuckInterface, DuckA)
    container.add_transient(DuckInterface, DuckB)
    container.add_transient(DuckInterface, DuckC)
    container.add_transient("duck", duck_d)
    return container


@fixture()
def container_with_singleton_classes(container):
    container.add_singleton(QuackBehavior, Sqeak)
    container.add_singleton(DuckInterface, DuckA)
    container.add_singleton(DuckInterface, DuckB)
    container.add_singleton(DuckInterface, DuckC)
    return container


def test_getting_obj_from_container(container_with_transient_classes):
    duck = container_with_transient_classes.get(DuckInterface)
    assert isinstance(duck, DuckInterface)
    assert isinstance(duck, DuckA)


def test_getting_factory_from_container(container_with_transient_classes):
    duck = container_with_transient_classes.get("duck")
    assert isinstance(duck, DuckInterface)
    assert isinstance(duck, DuckA)


def test_resolve_target(container_with_transient_classes):
    duck = container_with_transient_classes.resolve(DuckA)
    assert isinstance(duck, DuckInterface)
    assert isinstance(duck, DuckA)

    with raises(DependencyResolvingException):
        container_with_transient_classes.resolve(DuckC())


@pytest.mark.asyncio
async def test_async_resolve_target(container_with_transient_classes):
    async def test(duck: DuckA):
        return duck

    duck = await container_with_transient_classes.async_resolve(test)
    assert isinstance(duck, DuckInterface)
    assert isinstance(duck, DuckA)

    with raises(DependencyResolvingException):
        await container_with_transient_classes.async_resolve(DuckC)


def test_get_exception(container):
    with raises(DependencyNotFound):
        container.get("duck")


def test_getting_all_obj_from_container(container_with_transient_classes, container_with_singleton_classes):
    for duck in container_with_transient_classes.get_all(DuckInterface):
        assert isinstance(duck, DuckInterface)

    for duck in container_with_singleton_classes.get_all(DuckInterface):
        assert isinstance(duck, DuckInterface)


def test_transient_obj(container_with_transient_classes):
    duck_1 = container_with_transient_classes.get(DuckInterface)
    duck_2 = container_with_transient_classes.get(DuckInterface)
    assert duck_1 != duck_2
    assert id(duck_1) != id(duck_2)
    assert duck_1.__class__ == duck_2.__class__


def test_singleton_obj(container_with_singleton_classes):
    duck_1 = container_with_singleton_classes.get(DuckInterface)
    duck_2 = container_with_singleton_classes.get(DuckInterface)
    assert duck_1 == duck_2
    assert id(duck_1) == id(duck_2)
    assert duck_1.__class__ == duck_2.__class__


def test_context_scope(container):
    container.add_context(QuackBehavior, Sqeak)
    squeak = container.get(QuackBehavior)
    assert isinstance(squeak, QuackBehavior)
    assert squeak != container.get(QuackBehavior)

    def test_1(container):
        container.add_context(DuckInterface, DuckA)
        duck = container.get(DuckInterface)
        assert isinstance(duck, DuckInterface)

    def test_2(container):
        container.get(DuckInterface)

    ctx_1 = copy_context()
    ctx_1.run(test_1, container)

    ctx_2 = copy_context()
    with raises(DependencyNotFound):
        ctx_2.run(test_2, container)


def test_list_attr(container_with_singleton_classes: Container):
    def test_func(ducks: List[DuckInterface]):
        return ducks

    container_with_singleton_classes.add_transient("ducks_list", test_func)
    ducks_list_1 = container_with_singleton_classes.get("ducks_list")
    ducks_list_2 = container_with_singleton_classes.get_all(DuckInterface)
    assert ducks_list_1 == ducks_list_2


def test_get_target_attributes(container_with_singleton_classes: Container):
    def test_func(ducks: List[DuckInterface], duck: DuckInterface):
        return ducks, duck

    func_attributes = container_with_singleton_classes.get_target_attributes(test_func)
    assert list(func_attributes.keys()) == ["ducks", "duck"]

    func_values = list(func_attributes.values())
    assert isinstance(func_values[0], list)
    for duck in func_values[0]:
        assert isinstance(duck, DuckInterface)

    assert isinstance(func_values[1], DuckInterface)

    class_attributes = container_with_singleton_classes.get_target_attributes(DuckC())
    assert class_attributes is None


def test_len(container):
    container.add_transient(DuckInterface, DuckC)
    assert len(container) == 2


def test_iter_typing(container_with_singleton_classes: Container):
    def test_func(ducks: Iterator[DuckInterface]):
        return ducks

    container_with_singleton_classes.add_transient("ducks_list", test_func)
    duck_iterator = container_with_singleton_classes.get("ducks_list")
    ducks_list_1 = []
    for duck in duck_iterator:
        assert isinstance(duck, DuckInterface)
        ducks_list_1.append(duck)

    ducks_list_2 = container_with_singleton_classes.get_all(DuckInterface)
    assert ducks_list_1 == ducks_list_2


def test_tuping_not_resolving(container_with_singleton_classes: Container):
    class Test:
        pass

    def test_func(ducks: List[DuckInterface], a: Test):
        return ducks, a

    with raises(DependencyResolvingException):
        container_with_singleton_classes.get_target_attributes(test_func)


def test_override(container_with_singleton_classes):
    sqeak_mock: Sqeak = mock.Mock(spec=Sqeak)
    sqeak_mock.quack.return_value = "123"

    with container_with_singleton_classes.override(QuackBehavior, sqeak_mock):
        duck = container_with_singleton_classes.get(DuckInterface)
        assert duck.quack() == "123"

    class Test2:
        def quack(self):
            return "111"

    class Sqeak2(QuackBehavior):
        def __init__(self, test: Test2):
            self.test = test

        def quack(self):
            return self.test.quack()

    container_with_singleton_classes.add_transient(Test2, Test2)

    with container_with_singleton_classes.override(QuackBehavior, factory=Sqeak2, is_clear_cache=True):
        quack = container_with_singleton_classes.get(QuackBehavior)
        assert isinstance(quack, Sqeak2)
        duck = container_with_singleton_classes.get(DuckInterface)
        assert duck.quack() == "111"

    class Test:
        pass

    with raises(DependencyNotFound):
        with container_with_singleton_classes.override(Test, Sqeak2):
            pass
