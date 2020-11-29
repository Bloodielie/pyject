from abc import ABC, abstractmethod
from typing import List
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
        return "Quack_1"


class DuckA(DuckInterface):
    def __init__(self, squeak: QuackBehavior):
        self._quack_behavior = squeak

    def quack(self):
        return self._quack_behavior.quack()


class DuckC(DuckInterface):
    def quack(self):
        return "Quack_2"


container = Container()
container.add_singleton(QuackBehavior, Sqeak)
container.add_transient(DuckInterface, DuckA)
container.add_singleton(DuckInterface, DuckC)

duck = container.get(DuckInterface)
print(duck.quack())

ducks = container.get_all(DuckInterface)
for duck in ducks:
    print(duck.quack())


def test2(ducks: List[DuckInterface]):
    result_ = ""
    for duck in ducks:
        result_ += duck.quack()
    return result_


assert container.resolve(test2) == "Quack_1Quack_2"
