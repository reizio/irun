from enum import Enum


class IRunException(Exception):
    pass


class Matchers(str, Enum):

    # any matcher: ...
    # e.g: foo(...) => foo(MATCH_ONE)
    MATCH_ONE = "__match_one"

    # name matcher: $<identifier>
    # e.g: $foo => MATCH_NAME_foo
    MATCH_NAME = "__match_name"

    def can_match(self, name):
        return name.startswith(self)

    @staticmethod
    def load_name_match(name):
        assert self.is_name_match(name)
        name = name[len(self._MATCH_NAME) :]
        assert name[0] == "_"
        return name[1:]

    @staticmethod
    def store_name_match(name):
        return self._MATCH_NAME + "_" + name
