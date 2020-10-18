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


class DuckB(DuckInterface):
    def __init__(self, squeak: QuackBehavior):
        self._quack_behavior = squeak

    def quack(self):
        self._quack_behavior.quack()


class DuckC(DuckInterface):
    def quack(self):
        pass


def duck_d(squeak: QuackBehavior) -> DuckInterface:
    return DuckA(squeak)
