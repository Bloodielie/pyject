import inspect
from typing import Any, Union, List, Optional, Set, Tuple, Iterator

from pytest import fixture, raises

from pyject import DependencyResolvingException
from pyject.conditions import DefaultCondition, AnyCondition, UnionCondition, CollectionCondition, IteratorCondition


@fixture()
def list_typing():
    return List[str]


@fixture()
def set_typing():
    return Set[str]


@fixture()
def tuple_typing():
    return Tuple[str]


@fixture()
def union_typing():
    return Union[str, int]


@fixture()
def optional_typing():
    return Optional[str]


@fixture()
def iterator_typing():
    return Iterator[str]


def test_check_typing_default_condition(resolver_feick, list_typing):
    condition = DefaultCondition(resolver_feick)
    assert condition.check_typing(Any) is True


def test_check_typing_any_condition(resolver_feick, list_typing, union_typing):
    condition = AnyCondition(resolver_feick)
    assert condition.check_typing(Any) is True
    assert condition.check_typing(union_typing) is False
    assert condition.check_typing(list_typing) is False


def test_check_typing_union_condition(resolver_feick, list_typing, optional_typing, union_typing):
    condition = UnionCondition(resolver_feick)
    assert condition.check_typing(union_typing) is True
    assert condition.check_typing(optional_typing) is True
    assert condition.check_typing(Any) is False
    assert condition.check_typing(list_typing) is False


def test_check_typing_collection_condition(resolver_feick, list_typing, optional_typing, union_typing, set_typing, tuple_typing):
    condition = CollectionCondition(resolver_feick)
    assert condition.check_typing(union_typing) is False
    assert condition.check_typing(optional_typing) is False
    assert condition.check_typing(Any) is False
    assert condition.check_typing(list_typing) is True
    assert condition.check_typing(set_typing) is True
    assert condition.check_typing(tuple_typing) is True


def test_check_typing_iterator_condition(resolver_feick, list_typing, iterator_typing):
    condition = IteratorCondition(resolver_feick)
    assert condition.check_typing(union_typing) is False
    assert condition.check_typing(optional_typing) is False
    assert condition.check_typing(Any) is False
    assert condition.check_typing(list_typing) is False
    assert condition.check_typing(iterator_typing) is True


def test_get_attributes_any_condition(resolver_feick):
    condition = AnyCondition(resolver_feick)
    with raises(DependencyResolvingException):
        condition.get_attributes(Any)


def test_get_attributes_default_condition(resolver_feick, resolver_feick_2):
    condition = DefaultCondition(resolver_feick)
    with raises(DependencyResolvingException):
        condition.get_attributes(Any)

    condition = DefaultCondition(resolver_feick_2)
    assert condition.get_attributes(Any) == "test"
    assert isinstance(condition.get_attributes(Any), str)


def test_get_attributes_union_condition(resolver_feick, resolver_feick_2, optional_typing, union_typing):
    condition = UnionCondition(resolver_feick)
    assert condition.get_attributes(optional_typing) is None

    condition = UnionCondition(resolver_feick_2)
    assert condition.get_attributes(optional_typing) == "test"
    assert isinstance(condition.get_attributes(optional_typing), str)

    condition = UnionCondition(resolver_feick)
    with raises(DependencyResolvingException):
        condition.get_attributes(union_typing)

    condition = UnionCondition(resolver_feick_2)
    assert condition.get_attributes(union_typing) == "test"
    assert isinstance(condition.get_attributes(optional_typing), str)


def test_get_attributes_collection_condition(resolver_feick, resolver_feick_2, list_typing):
    condition = CollectionCondition(resolver_feick)
    with raises(DependencyResolvingException):
        condition.get_attributes(list_typing)

    condition = CollectionCondition(resolver_feick_2)
    assert condition.get_attributes(list_typing) == ["test"]
    assert isinstance(condition.get_attributes(list_typing), list)
    assert isinstance(condition.get_attributes(list_typing)[0], str)


def test_get_attributes_iterator_condition(resolver_feick, resolver_feick_2, iterator_typing):
    condition = IteratorCondition(resolver_feick)
    iterator = condition.get_attributes(iterator_typing)
    assert inspect.isgenerator(iterator) is True
    for _ in iterator:
        pass

    condition = IteratorCondition(resolver_feick_2)
    iterator = condition.get_attributes(iterator_typing)
    for value in iterator:
        assert value == "test"
        assert isinstance(value, str)
