from abc import ABC, abstractmethod
from typing import List, Sequence, Optional, Union, Iterator
from pyject import Container, ForwardRef



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


# Sequence: ("Set", "List", "Tuple", "FrozenSet", "Sequence")
def list_typing(ducks: List[DuckInterface]):
    result_ = ""
    for duck in ducks:
        result_ += duck.quack()
    return result_


def sequence_typing(ducks: Sequence[DuckInterface]):
    result_ = ""
    for duck in ducks:
        result_ += duck.quack()
    return result_


assert container.resolve(list_typing) == "Quack_1Quack_2"
assert container.resolve(sequence_typing) == "Quack_1Quack_2"
# Union: (Union, Optional)
def union_typing(quack: Union[QuackBehavior, DuckInterface]):
    return quack


def optional_typing(test: Optional[List]):
    return test


assert isinstance(container.resolve(union_typing), QuackBehavior)
assert container.resolve(optional_typing) is None
# ForwardRef
class Test:
    def __init__(self, test2: ForwardRef["Test2"]):
        self.test2 = test2

    def test(self):
        return self.test2.test2()


class Test2:
    def __init__(self, test: ForwardRef[Test]):
        self.test = test

    def test2(self):
        return "123"


container.add_singleton(Test, Test)
container.add_singleton(Test2, Test2)

test = container.get(Test)
assert isinstance(test, Test)
assert isinstance(test.test2, ForwardRef)
assert isinstance(test.test2.test, ForwardRef)
assert test.test() == "123"
assert test.test() == test.test2.test2()
# Iterator
def iterator_typing(ducks: Iterator[DuckInterface]):
    result_ = ""
    for duck in ducks:
        result_ += duck.quack()
    return result_
assert container.resolve(iterator_typing) == "Quack_1Quack_2"
