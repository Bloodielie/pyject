from unittest import mock

from pytest import fixture

from pyject.collections import DependencyStorage
from pyject.resolver import Resolver


@fixture()
def resolver_feick():
    resolver_mock = mock.Mock(spec=Resolver)
    resolver_mock.get_resolved_dependencies.return_value = []
    return resolver_mock


@fixture()
def resolver_feick_2():
    resolver_mock = mock.Mock(spec=Resolver)
    resolver_mock.get_resolved_dependencies.return_value = ["test"]
    return resolver_mock


@fixture()
def dependency_storage_feick():
    dependency_storage_mock = mock.Mock(spec=DependencyStorage)
    return dependency_storage_mock
