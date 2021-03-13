import tokenize
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

from irun.run import compile_irun

INDENT = " " * 4
CASE_PREFIX = "# case:"
CURRENT_DIR = Path(__file__).parent


@dataclass
class TestCase:
    name: str
    source: str
    expected: str

    @classmethod
    def from_source_lines(cls, source_lines):
        metadata, source, expected, *_ = source_lines
        _, _, name = metadata.partition(CASE_PREFIX)
        return cls(name.strip(), source, expected)

    def execute(self):
        result = compile_irun(self.source)
        succeed = result.strip() == self.expected.strip()
        if not succeed:
            print("execution failed for: ", repr(self.name))
            print(INDENT, "result:")
            print(INDENT * 2, result)
            print(INDENT, "expected:")
            print(INDENT * 2, self.expected)

        return succeed


def prepare_cases(test_files):
    for test_file in test_files:
        lines = []
        with open(test_file) as stream:
            lines = stream.readlines()
            stream.seek(0)
            tokens = tuple(tokenize.generate_tokens(stream.readline))

        locations = []
        for token in tokens:
            if token.type == tokenize.COMMENT and token.string.startswith(CASE_PREFIX):
                locations.append(token.start[0] - 1)

        for start, end in zip(locations, locations[1:]):
            source_lines = lines[start:end]
            yield TestCase.from_source_lines(source_lines)


def run_tests(test_dir):
    failed = False
    for n, case in enumerate(prepare_cases(test_dir.glob("**/*.irun"))):
        failed |= not case.execute()
    if not failed:
        print(f"{n} cases successfully passed")
    return failed


def main(argv=None):
    parser = ArgumentParser()
    parser.add_argument("--test-dir", default=CURRENT_DIR / "cases")

    options = parser.parse_args(argv)
    return run_tests(options.test_dir)


if __name__ == "__main__":
    exit(main())
