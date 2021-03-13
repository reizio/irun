from enum import Enum


class IRunException(Exception):
    pass


class Matchers(str, Enum):

    # any matcher: ...
    # e.g: foo(...) => foo(MATCH_ONE)
    MATCH_ONE = "__match_one"

    # all matcher: ***
    # e.g: foo(***) => foo(MATCH_ANY)
    MATCH_ANY = "__match_any"

    # name matcher: $<identifier>
    # e.g: $foo => MATCH_NAME_foo
    MATCH_NAME = "__match_name"

    def can_match(self, name):
        return name.startswith(self)

    def load(self, name):
        assert self.can_match(name)
        name = name[len(self) :]
        assert name[0] == "_"
        return name[1:]

    def store(self, name):
        return self + "_" + name
