from typing import List

from pyject.exception import DependencyNotFound

from pytest import fixture, raises

from pyject.container import Container
from tests.classes import QuackBehavior, Sqeak, DuckInterface, DuckA, DuckB, DuckC, duck_d


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


def test_len(container):
    container.add_transient(DuckInterface, DuckC)
    assert len(container) == 2
