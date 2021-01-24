import ast
from argparse import ArgumentParser, FileType

from irun.compiler import compile_node, construct
from irun.preprocessor import transpile


def compile_irun(source):
    sanitized_source = transpile(source)

    tree = ast.parse(sanitized_source)
    if len(tree.body) == 1:
        tree = tree.body[0]

    reiz_node = compile_node(tree)
    return reiz_node


def main(argv=None):
    parser = ArgumentParser()
    parser.add_argument("source", type=FileType())

    options = parser.parse_args(argv)
    with options.source as stream:
        reiz_node = compile_irun(stream.read())
    print(construct(reiz_node))


if __name__ == "__main__":
    main()
