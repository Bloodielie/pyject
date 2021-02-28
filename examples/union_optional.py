from typing import Union, Optional, TypeVar

from examples.classes import QuackBehavior, DuckInterface, Sqeak
from pyject import Container


T = TypeVar("T")


class DuckA(DuckInterface):
    def __init__(self, quack: Union[QuackBehavior, None]):
        self.quack_ = quack

    def quack(self):
        return self.quack_.quack()


class DuckB(DuckInterface):
    def __init__(self, quack: Optional[QuackBehavior]):
        self._quack = quack

    def quack(self):
        if self._quack is not None:
            return self._quack.quack()


container = Container()
container.add_singleton(QuackBehavior, Sqeak)
container.add_transient(DuckInterface, DuckA)

result = container.get(DuckInterface).quack()
print(result)
assert result == "Quack_1"


container = Container()
container.add_transient(DuckInterface, DuckB)

result = container.get(DuckInterface).quack()
print(result)
assert result is None
