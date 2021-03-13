from argparse import ArgumentParser, FileType

from irun.compiler import compile_node, construct
from irun.parser import parse


def compile_irun(source):
    tree = parse(source)
    reiz_node = compile_node(tree)
    return reiz_node


def main(argv=None):
    parser = ArgumentParser()
    parser.add_argument("source", type=FileType())

    options = parser.parse_args(argv)
    with options.source as stream:
        compile_irun(stream.read())
    print(construct(reiz_node))


if __name__ == "__main__":
    main()
