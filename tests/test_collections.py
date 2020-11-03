from typing import Any

from pytest import raises

from pyject import DependencyResolvingException
from pyject.collections import ConditionCollections
from pyject.conditions import AnyCondition, DefaultCondition


def test_add_condition(resolver_feick):
    collection = ConditionCollections(resolver_feick)
    assert len(collection) == 0
    collection.add(AnyCondition)
    assert len(collection) == 1

    for condition in collection:
        assert isinstance(condition, AnyCondition)


def test_conditions_in_init(resolver_feick):
    collection = ConditionCollections(resolver_feick, [AnyCondition])
    assert len(collection) == 1
    for condition in collection:
        assert isinstance(condition, AnyCondition)


def test_default_condition_in_init(resolver_feick):
    collection = ConditionCollections(resolver_feick, default_condition=DefaultCondition)
    assert len(collection) == 1
    for condition in collection:
        assert isinstance(condition, DefaultCondition)


def test_find(resolver_feick, resolver_feick_2):
    collection = ConditionCollections(resolver_feick)
    assert collection.find(Any) is None

    collection = ConditionCollections(resolver_feick, default_condition=DefaultCondition)
    with raises(DependencyResolvingException):
        collection.find(Any)

    collection = ConditionCollections(resolver_feick_2, default_condition=DefaultCondition)
    assert collection.find(Any) == "test"
