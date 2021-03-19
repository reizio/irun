from dataclasses import dataclass, field
from functools import singledispatch
from typing import Any, Dict

from irun.parser import ast


def construct(node):
    if isinstance(node, Matcher):
        return node.construct()
    else:
        return node


class Matcher:
    ...


class AnyMatcher(Matcher):
    def construct(self):
        return "..."


class AllMatcher(Matcher):
    def construct(self):
        return "*..."


@dataclass
class ValueMatcher(Matcher):
    value: Any


class SequenceMatcher(ValueMatcher):
    def construct(self):
        assert isinstance(self.value, list)
        source = "["
        source += ", ".join(construct(item) for item in self.value)
        source += "]"
        return source


class LiteralMatcher(ValueMatcher):
    def construct(self):
        return repr(self.value)


class ReferenceMatcher(ValueMatcher):
    def construct(self):
        return "~" + self.value


@dataclass
class Context(ValueMatcher):
    fields: Dict[str, Matcher] = field(default_factory=dict)

    @classmethod
    def from_node(cls, node):
        context = cls(type(node).__name__)
        for field, value in ast.iter_fields(node):
            context.describe(field, value)
        return context

    def describe(self, field, value):
        if value is None:
            return None

        matcher = None
        if isinstance(value, list):
            matcher = SequenceMatcher([compile_node(node) for node in value])
        elif isinstance(value, (str, int)):
            matcher = LiteralMatcher(value)
        elif isinstance(value, ast.AST):
            matcher = compile_node(value)

        if matcher is not None:
            self.fields[field] = matcher

    def remove(self, field):
        return self.fields.pop(field, None)

    def construct(self):
        source = self.value
        source += "("
        source += ", ".join(
            f"{key}={construct(value)}" for key, value in self.fields.items()
        )
        source += ")"
        return source


@singledispatch
def compile_node(node):
    context = Context.from_node(node)
    return context


@compile_node.register(ast.IgnoreOne)
def compile_ignore_any(node):
    return AnyMatcher()


@compile_node.register(ast.IgnoreAny)
def compile_ignore_all(node):
    return AllMatcher()


@compile_node.register(ast.Reference)
def compile_reference(node):
    return ReferenceMatcher(node.id)


@compile_node.register(ast.expr)
def compile_expr(node):
    context = Context.from_node(node)

    # ctx is more about semantics than the structure
    # of the source code. For nodes like Name/Attribute
    # we will clear this field in order to match all
    # similiar structures.
    context.remove("ctx")
    context = dispatch_expression(node, context)

    return context


@singledispatch
def dispatch_expression(node, context):
    return context


@dispatch_expression.register(ast.Call)
def dispatch_call(node, context):
    if len(node.args) >= 1 and isinstance(node.args[-1], ast.IgnoreAny):
        context.remove("keywords")
    return context
