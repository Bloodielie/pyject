from pyject import Container, ForwardRef


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


container = Container()
container.add_singleton(Test, Test)
container.add_singleton(Test2, Test2)

test = container.get(Test)
assert isinstance(test, Test)
assert isinstance(test.test2, ForwardRef)
assert isinstance(test.test2.test, ForwardRef)
assert test.test() == "123"
assert test.test() == test.test2.test2()
