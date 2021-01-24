import ast
from dataclasses import dataclass, field
from functools import singledispatch
from typing import Any, Dict, List

from irun.base import Matchers


def construct(value):
    if isinstance(value, _ReizObject):
        return value.construct()
    elif isinstance(value, list):
        return "[" + ", ".join(construct(item) for item in value) + "]"
    else:
        return repr(value)


class _ReizObject:
    def kv_view(self, items):
        for key, value in items:
            yield f"{key}={construct(value)}"


@dataclass
class ReizNode(_ReizObject):
    matcher: str
    fields: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_ast(cls, node):
        return cls(type(node).__name__)

    def add_field(self, field, value):
        if value:
            self.fields[field] = value

    def compile_list(self, field, nodes):
        self.add_field(field, compile_list(nodes))

    def compile_field(self, field, node):
        if node is not None:
            self.add_field(field, compile_node(node))

    def construct(self):
        source = self.matcher
        source += "("
        source += ", ".join(self.kv_view(self.fields.items()))
        source += ")"
        return source


@dataclass
class ReizCall(_ReizObject):
    func: str
    pos_args: List[Any] = field(default_factory=list)
    key_args: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, func, *pos_args, **key_args):
        self.func = func
        self.pos_args = list(pos_args)
        self.key_args = key_args

    def construct(self):
        source = self.func
        source += "("
        source += ", ".join(self.pos_args + list(self.kv_view(self.key_args.items())))
        source += ")"
        return source


def compile_list(nodes):
    return [compile_node(node) for node in nodes]


def body_exists(items):
    return not (
        len(items) == 1
        and isinstance(expr := items[0], ast.Expr)
        and isinstance(name := expr.value, ast.Name)
        and name.id == Matchers.MATCH_ANY
    )


def if_exists(reiz_node):
    if reiz_node.fields:
        return reiz_node
    else:
        return None


@singledispatch
def compile_node(node):
    raise ValueError(f"Unsupported node: {type(node).__name__}")


@compile_node.register(ast.FunctionDef)
def compile_function(node):
    # FunctionDef(identifier name, arguments args,
    #             stmt* body, expr* decorator_list, expr? returns,
    #             string? type_comment)
    reiz_node = ReizNode.from_ast(node)

    # identifier name
    if node.name != Matchers.MATCH_ONE:
        reiz_node.add_field("name", node.name)

    # arguments args
    reiz_node.compile_field("args", node.args)

    # stmt* body
    if body_exists(node.body):
        reiz_node.add_field("body", compile_list(node.body))

    # expr* decorator_list
    reiz_node.compile_list("decorator_list", node.decorator_list)

    # expr? returns
    reiz_node.compile_field("returns", node.returns)

    # string? type_comment
    reiz_node.compile_field("type_comment", node.type_comment)
    return reiz_node


@compile_node.register(ast.arguments)
def compile_arguments(node):
    # (arg* posonlyargs, arg* args, arg? vararg, arg* kwonlyargs,
    #  expr* kw_defaults, arg? kwarg, expr* defaults)
    reiz_node = ReizNode.from_ast(node)

    # arg* posonlyargs
    reiz_node.compile_list("posonlyargs", node.posonlyargs)

    # arg* args
    reiz_node.compile_list("args", node.args)

    # arg? vararg
    reiz_node.compile_field("vararg", node.vararg)

    # arg* kwonlyargs
    reiz_node.compile_list("kwonlyargs", node.kwonlyargs)

    # arg* kw_defaults
    reiz_node.compile_list("kw_defaults", node.kw_defaults)

    # arg? kwarg
    reiz_node.compile_field("kwarg", node.kwarg)

    # arg* defaults
    reiz_node.compile_list("defaults", node.defaults)

    return if_exists(reiz_node)


@compile_node.register(ast.For)
def compile_for(node):
    # For(expr target, expr iter, stmt* body, stmt* orelse,
    #     string? type_comment)
    reiz_node = ReizNode.from_ast(node)

    # expr target
    reiz_node.compile_field("target", node.target)

    # expr iter
    reiz_node.compile_field("iter", node.iter)

    # stmt* body
    if body_exists(node.body):
        reiz_node.compile_list("body", node.body)

    # stmt* orelse
    if body_exists(node.orelse):
        reiz_node.compile_list("orelse", node.orelse)
    else:
        reiz_node.add_field("orelse", ReizCall("LEN", min=1))

    # string? type_comment
    reiz_node.compile_field("type_comment", node.type_comment)
    return reiz_node


@compile_node.register(ast.Name)
def compile_name(node):
    # Name(identifier id, expr_context ctx)
    reiz_node = ReizNode.from_ast(node)

    # identifier id
    if node.id != Matchers.MATCH_ONE:
        reiz_node.add_field("id", node.id)

    return if_exists(reiz_node)


@compile_node.register(ast.Call)
def compile_call(node):
    # Call(expr func, expr* args, keyword* keywords)
    reiz_node = ReizNode.from_ast(node)

    # expr func
    reiz_node.compile_field("func", node.func)

    # expr* args
    reiz_node.compile_list("args", node.args)

    # keyword* keywords
    reiz_node.compile_list("keywords", node.keywords)
    return reiz_node


@compile_node.register(ast.Expr)
def compile_expr(node):
    # Expr(expr value)
    reiz_node = ReizNode.from_ast(node)

    # expr value
    reiz_node.compile_field("value", node.value)

    return reiz_node
