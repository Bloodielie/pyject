from timeit import timeit

from pyject import Container
from abc import ABC, abstractmethod


class DuckInterface(ABC):
    @abstractmethod
    def quack(self):
        raise NotImplementedError()


class QuackBehavior(ABC):
    @abstractmethod
    def quack(self):
        raise NotImplementedError()


class Sqeak(QuackBehavior):
    def quack(self):
        pass


class DuckA(DuckInterface):
    def __init__(self, squeak: QuackBehavior):
        self._quack_behavior = squeak

    def quack(self):
        self._quack_behavior.quack()


class DuckC(DuckInterface):
    def quack(self):
        pass


def get_globals(container: Container):
    return {"container": container, "DuckInterface": DuckInterface}


def setup_transient():
    container = Container()
    container.add_transient(QuackBehavior, Sqeak)
    container.add_transient(DuckInterface, DuckA)
    container.add_transient(DuckInterface, DuckC)
    return container


def setup_singleton():
    container = Container()
    container.add_singleton(QuackBehavior, Sqeak)
    container.add_singleton(DuckInterface, DuckA)
    container.add_singleton(DuckInterface, DuckC)
    return container


def setup_big_transient():
    container = Container()
    container.add_transient(QuackBehavior, Sqeak)
    for _ in range(20):
        container.add_transient(DuckInterface, DuckA)
    for _ in range(20):
        container.add_transient(DuckInterface, DuckC)
    return container


def setup_big_singleton():
    container = Container()
    container.add_singleton(QuackBehavior, Sqeak)
    for _ in range(20):
        container.add_singleton(DuckInterface, DuckA)
    for _ in range(20):
        container.add_singleton(DuckInterface, DuckC)
    return container


def get_time(method: str, container: Container):
    return timeit(f"container.{method}(DuckInterface)", globals=get_globals(container), number=number)


def get_ops(time):
    return 1 / (time / number)


number = 1000

container = setup_transient()

print("get transient", get_ops(get_time("get", container)))  # 6500
print("get_all transient", get_ops(get_time("get_all", container)))  # 3802

container = setup_singleton()

print("get singleton", get_ops(get_time("get", container)))  # 437690
print("get_all singleton", get_ops(get_time("get_all", container)))  # 356515

container = setup_big_transient()

print("get big_transient", get_ops(get_time("get", container)))  # 5439
print("get_all big_transient", get_ops(get_time("get_all", container)))  # 153

container = setup_big_singleton()

print("get big_singleton", get_ops(get_time("get", container)))  # 432372
print("get_all big_singleton", get_ops(get_time("get_all", container)))  # 38886
