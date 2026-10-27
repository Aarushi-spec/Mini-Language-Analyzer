
import re
from dataclasses import dataclass


@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int


KEYWORDS = {
    "int": "TYPE",
    "float": "TYPE",
    "string": "TYPE",
    "bool": "TYPE",
    "print": "PRINT",
    "if": "IF",
    "else": "ELSE",
    "true": "BOOLEAN",
    "false": "BOOLEAN",
}

TOKEN_PATTERN = re.compile(
    r"(?P<WHITESPACE>[ \t\r]+)"
    r"|(?P<NEWLINE>\n)"
    r"|(?P<COMMENT>//[^\n]*)"
    r'|(?P<STRING>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')'
    r"|(?P<NUMBER>\d+\.\d+|\d+)"
    r"|(?P<IDENTIFIER>[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<OPERATOR>==|!=|<=|>=|[+\-*/%=<>])"
    r"|(?P<SEPARATOR>[();{},])"
)


def tokenize(source_code):
    tokens = []
    errors = []

    position = 0
    line = 1
    column = 1

    while position < len(source_code):
        match = TOKEN_PATTERN.match(source_code, position)

        if not match:
            character = source_code[position]

            errors.append({
                "line": line,
                "column": column,
                "message": f"Unexpected character: {character!r}"
            })

            position += 1

            if character == "\n":
                line += 1
                column = 1
            else:
                column += 1

            continue

        value = match.group()
        token_type = match.lastgroup
        token_line = line
        token_column = column

        if token_type == "NEWLINE":
            line += 1
            column = 1
            position = match.end()
            continue

        if token_type in ("WHITESPACE", "COMMENT"):
            column += len(value)
            position = match.end()
            continue

        if token_type == "IDENTIFIER":
            token_type = KEYWORDS.get(value, "IDENTIFIER")

        elif token_type == "NUMBER":
            token_type = "FLOAT_LITERAL" if "." in value else "INT_LITERAL"

        elif token_type == "STRING":
            token_type = "STRING_LITERAL"

        elif token_type == "OPERATOR":
            token_type = "OPERATOR"

        elif token_type == "SEPARATOR":
            token_type = "SEPARATOR"

        tokens.append(
            Token(
                type=token_type,
                value=value,
                line=token_line,
                column=token_column
            )
        )

        column += len(value)
        position = match.end()

    return tokens, errors
