from typing import Sequence

from examples.classes import QuackBehavior, Sqeak, DuckInterface
from pyject import Container


class Sqeak2(QuackBehavior):
    def quack(self):
        return "Quack_2"


class Sqeak3(QuackBehavior):
    def quack(self):
        return "Quack_3"


class DuckA(DuckInterface):
    def __init__(self, sqeaks: Sequence[QuackBehavior]):  # maybe List[QuackBehavior], Tuple[QuackBehavior] e.t.c
        self.sqeaks = sqeaks

    def quack(self):
        return " ".join([sqeak.quack() for sqeak in self.sqeaks])


container = Container()
container.add_singleton(QuackBehavior, Sqeak)
container.add_singleton(QuackBehavior, Sqeak2)
container.add_singleton(QuackBehavior, Sqeak3)
container.add_transient(DuckInterface, DuckA)

duck = container.get(DuckInterface)
print(duck.quack())
assert duck.quack() == "Quack_1 Quack_2 Quack_3"
