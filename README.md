# pyject

## What is Pyject?
Pyject is a IocContainer for Python.

It helps implementing the dependency injection principle.

## Installation
The package is available on the PyPi:
```bash
pip install pyjectt
```

## Examples
1. [Base](#Base_example)
2. Non-default types
   + [Sequence: ("Set", "List", "Tuple", "FrozenSet", "Sequence")](#Sequence_example)
   + [Union: (Union, Optional)](#Union_example)
   + [ForwardRef](#ForwardRef_example)
   + [Iterator](#Iterator_example)

<a name="Base_example"></a>
### Base
```python
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
```
## Non-default types
<a name="Sequence_example"></a>

### Sequence
```python
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
```
<a name="Union_example"></a>
### Union
```python
def union_typing(quack: Union[QuackBehavior, DuckInterface]):
    return quack

def optional_typing(test: Optional[List]):
    return test

assert isinstance(container.resolve(union_typing), QuackBehavior)
assert container.resolve(optional_typing) is None
```
<a name="ForwardRef_example"></a>
### ForwardRef
```python
from pyject.types import ForwardRef

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
```
<a name="Iterator_example"></a>
### Iterator
```python
def iterator_typing(ducks: Iterator[DuckInterface]):
    result_ = ""
    for duck in ducks:
        result_ += duck.quack()
    return result_

assert container.resolve(iterator_typing) == "Quack_1Quack_2"
```