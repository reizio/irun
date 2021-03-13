from argparse import ArgumentParser
from pathlib import Path

CURRENT_DIR = Path(__file__).parent


def prepare_cases(test_files):
    for test_file in test_files:
        test_file.read_text().splitlines()


def run_tests(test_dir):
    prepare_cases(test_dir.glob("**/*.irun"))


def main():
    parser = ArgumentParser()
    parser.add_argument("test_dir", default=CURRENT_DIR / "tests")

    options = parser.parse_args()
    run_tests(options.test_dir)
