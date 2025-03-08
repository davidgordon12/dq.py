import os
import sys
from enum import Enum
from typing import List, Dict, NewType, Union

# Allowed union types = int | float | str | bool
Value = NewType('Value', Union[int, float, str, bool])


class TokenType(Enum):
    FIELD = 1,
    VALUE = 2


class Token:
    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value


def generic_error(idx):
    print(f"Invalid JSON at index {idx}. Exiting")
    exit(1)


def serialize(path: os.path):
    file = open(path, "r")
    tokenize(str(file.read()))


def tokenize(source: str) -> List[str]:
    tokens = []

    def parse_field(start_idx):
        curr = start_idx
        while curr < len(source) and source[curr] != '"':
            curr += 1
        tokens.append(Token(TokenType.FIELD, source[start_idx:curr]))
        return curr+1

    def read_str(start_idx):
        curr = start_idx
        while curr < len(source) and source[curr] != '"':
            curr += 1
        tokens.append(Token(TokenType.VALUE, source[start_idx:curr]))
        return curr+1

    def read_number(start_idx):
        curr = start_idx
        while (curr < len(source) and source[curr].isnumeric() or
                source[curr] == '.'):
            curr += 1
        tokens.append(Token(TokenType.VALUE, Value(source[start_idx:curr])))
        return curr

    if len(source) < 2 or source[0] != '{' or source[-2] != '}':
        generic_error(0)

    curr = 1  # skip the leading brace

    while source[curr] != '}':
        while (curr < len(source) and source[curr] == ' '
               or source[curr] == '\t' or source[curr] == '\r'
               or source[curr] == '\n'):
            curr += 1

        if source[curr] == '"':
            curr = parse_field(curr+1)

        # First str read should be followed by a semicolon
        if source[curr] != ":":
            generic_error(curr)
        curr += 1

        while (curr < len(source) and source[curr] == ' '
               or source[curr] == '\t' or source[curr] == '\r'
               or source[curr] == '\n'):
            curr += 1

        # curr should be at an actual value now.
        if source[curr].isnumeric():
            curr = read_number(curr)
        elif source[curr] == '"':
            curr = read_str(curr+1)
        curr += 1

        if source[curr] == ',':
            curr += 1

    parse(tokens)


def parse(tokens: List[Token]) -> Dict[str, Value]:
    d = {}
    for k, v in zip(
            [k for k in tokens if k.token_type == TokenType.FIELD],
            [v for v in tokens if v.token_type == TokenType.VALUE]):
        d[k.value] = v.value


if len(sys.argv) < 2:
    print("Usage: python dq.py <file_path>")

path = sys.argv[1]
serialize(path)
