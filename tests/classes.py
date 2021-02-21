from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pyject.types import ForwardRef

T = TypeVar("T")


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
        return self._quack_behavior.quack()


class DuckB(DuckInterface):
    def __init__(self, squeak: QuackBehavior):
        self._quack_behavior = squeak

    def quack(self):
        return self._quack_behavior.quack()


class DuckC(DuckInterface):
    def quack(self):
        pass


class Test1:
    def __init__(self, test2: ForwardRef["Test2"]):
        self.test2 = test2

    def test1(self):
        return self.test2.test2()


class Test2:
    def __init__(self, test1: ForwardRef[Test1]):
        self.test1 = test1

    def test2(self):
        return "123"


def duck_d(squeak: QuackBehavior) -> DuckInterface:
    return DuckA(squeak)


class GenericDuckInterface(Generic[T], ABC):
    @abstractmethod
    def quack(self):
        raise NotImplementedError()


class DuckA2(GenericDuckInterface):
    def __init__(self, squeak: QuackBehavior):
        self._quack_behavior = squeak

    def quack(self):
        return self._quack_behavior.quack()


class DuckB2(GenericDuckInterface):
    def __init__(self, squeak: QuackBehavior):
        self._quack_behavior = squeak

    def quack(self):
        return self._quack_behavior.quack()
