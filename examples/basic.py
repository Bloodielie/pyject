from abc import ABC, abstractmethod

from pyject import Container


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
        print("Quack_1")


class DuckA(DuckInterface):
    def __init__(self, squeak: QuackBehavior):
        self._quack_behavior = squeak

    def quack(self):
        self._quack_behavior.quack()


class DuckC(DuckInterface):
    def quack(self):
        print("Quack_2")


container = Container()
container.add_singleton(QuackBehavior, Sqeak)
container.add_transient(DuckInterface, DuckA)
container.add_singleton(DuckInterface, DuckC)

duck = container.get(DuckInterface)
duck.quack()

ducks = container.get_all(DuckInterface)
for duck in ducks:
    duck.quack()

print(container.get(DuckInterface) != container.get(DuckInterface))
