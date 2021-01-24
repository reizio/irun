from enum import Enum


class IRunException(Exception):
    pass


class Matchers(str, Enum):

    MATCH_ONE = "__match_one"
    MATCH_ANY = "__match_any"

    # name matcher: __bound_name_$name
    # e.g: $foo => __bound_name_foo
    #      $_bar => __bound_name__bar

    _MATCH_NAME = "__match_name"

    @staticmethod
    def is_name_match(name):
        return name.startswith(self._MATCH_NAME)

    @staticmethod
    def load_name_match(name):
        assert self.is_name_match(name)
        name = name[len(self._MATCH_NAME) :]
        assert name[0] == "_"
        return name[1:]

    @staticmethod
    def store_name_match(name):
        return self._MATCH_NAME + "_" + name
