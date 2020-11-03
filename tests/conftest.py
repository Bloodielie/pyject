from pytest import fixture


@fixture()
def resolver_feick():
    class Resolver:
        def get_resolved_dependencies(self, typing):
            return []
    return Resolver()


@fixture()
def resolver_feick_2():
    class Resolver:
        def get_resolved_dependencies(self, typing):
            return ["test"]
    return Resolver()
