import io
import re
import token
import tokenize
from argparse import ArgumentParser, FileType
from dataclasses import dataclass

from irun.base import IRunException, Matchers


@dataclass
class PreprocessError(IRunException):
    message: str
    lineno: int
    col_offset: int
    end_lineno: int
    end_col_offset: int


def register_tokens(token_dict):
    def next_token_slot():
        index = max(token.tok_name.keys(), default=0)
        return index + 1

    escaped_tokens = []
    for name, value in token_dict.items():
        slot = next_token_slot()

        setattr(token, name, slot)
        token.tok_name[slot] = name
        token.EXACT_TOKEN_TYPES[value] = slot

        escaped_tokens.append(re.escape(value))

    tokenize.PseudoToken = tokenize.Whitespace + tokenize.group(
        *escaped_tokens,
        tokenize.PseudoExtras,
        tokenize.Number,
        tokenize.Funny,
        tokenize.ContStr,
        tokenize.Name,
    )


register_tokens({"DOLLAR": "$", "TRIPLESTAR": "***"})

BOUND_NAME_PREFIX = "__bound_name"
TRANSLATION_SCHEMA = {
    token.ELLIPSIS: (token.NAME, Matchers.MATCH_ONE),
    token.TRIPLESTAR: (token.NAME, Matchers.MATCH_ANY),
}


def _transpile_tokens(original_tokens):
    new_tokens = []

    cursor = 0
    while cursor < len(original_tokens):
        current_token = original_tokens[cursor]
        if special_identifier := TRANSLATION_SCHEMA.get(current_token.exact_type):
            new_tokens.append(special_identifier)
        elif current_token.exact_type == token.DOLLAR:
            # This should always be token.ENDMARKER, but just incase
            if cursor + 1 == len(original_tokens):
                raise PreprocessError("EOF", *current_token.start, *current_token.end)

            next_token = original_tokens[cursor + 1]
            if next_token.exact_type != token.NAME:
                raise PreprocessError(
                    f"Expected a NAME token, got {token.tok_name[next_token.exact_type]}",
                    *current_token.start,
                    *current_token.end,
                )

            next_token = next_token._replace(
                string=Matchers.store_name_match(next_token.string)
            )
            new_tokens.append(next_token)
            cursor += 1
        else:
            new_tokens.append(current_token)
        cursor += 1
    return new_tokens


def transpile(source):
    source_buffer = io.StringIO(source)
    token_iterator = tokenize.generate_tokens(source_buffer.readline)
    new_tokens = _transpile_tokens(tuple(token_iterator))
    return tokenize.untokenize(token[:2] for token in new_tokens)


def main(argv=None):
    parser = ArgumentParser()
    parser.add_argument("source", type=FileType())

    options = parser.parse_args()
    with options.source as stream:
        print(transpile(stream.read()))


if __name__ == "__main__":
    exit(main())
