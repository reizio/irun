import ast
from argparse import ArgumentParser, FileType
from functools import partial, partialmethod

from irun.base import Matchers
from irun.preprocessor import transpile

DEFINITION_TYPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


class Ignore(ast.AST):
    _fields = ()
    _attributes = ("lineno", "col_offset", "end_lineno", "end_col_offset")


class Reference(ast.expr):
    _fields = ("id",)


def compose_transformers(*partials):
    def composer(self, node):
        result = node
        for partial in partials:
            result = partial(self, result)
        return result

    return composer


def maybe_reference(name, flows_from):
    if Matchers.MATCH_ONE.can_match(name):
        node = Ignore()
    elif Matchers.MATCH_NAME.can_match(name):
        node = Reference(Matchers.load_name_match(name))
    else:
        return None

    return ast.copy_location(node, flows_from)


class ASTRestructurer(ast.NodeTransformer):
    def add_definition(self, node, field):
        identifier = getattr(node, field)
        if identifier is not None:
            identifier = maybe_reference(identifier, node)
            setattr(node, field, identifier)
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if reference := maybe_reference(node.id, node):
            return reference
        else:
            return node

    visit_ClassDef = partialmethod(add_definition, field="name")
    visit_FunctionDef = partialmethod(add_definition, field="name")
    visit_AsyncFunctionDef = partialmethod(add_definition, field="name")

    visit_Attribute = partialmethod(add_definition, field="attr")
    visit_ImportFrom = partialmethod(add_definition, field="module")

    visit_arg = partialmethod(add_definition, field="arg")
    visit_keyword = partialmethod(add_definition, field="arg")
    visit_excepthandler = partialmethod(add_definition, field="name")

    visit_alias = compose_transformers(
        partial(add_definition, field="name"), partial(add_definition, field="asname")
    )


def parse(source):
    source = transpile(source)
    tree = ast.parse(source)
    restructurer = ASTRestructurer()
    return restructurer.visit(tree)


def main(argv=None):
    parser = ArgumentParser()
    parser.add_argument("source", type=FileType())

    options = parser.parse_args()
    with options.source as stream:
        print(ast.dump(parse(stream.read())))


if __name__ == "__main__":
    exit(main())
