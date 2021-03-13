from argparse import ArgumentParser

from irun.compiler import compile_node, construct
from irun.parser import parse


def compile_irun(source):
    tree = parse(source)
    rql_context = compile_node(tree)
    return rql_context


def main(argv=None):
    parser = ArgumentParser()
    parser.add_argument("-c", "--cli", help="input from command line")
    parser.add_argument("-f", "--file", help="input from file")

    options = parser.parse_args(argv)
    if options.cli:
        source = options.cli
    elif options.file:
        with open(options.file) as stream:
            source = stream.read()
    else:
        raise ValueError("run.py expects either -c/--cli or -f/--file to operate")

    rql_context = compile_irun(source)
    print(construct(rql_context))


if __name__ == "__main__":
    main()
