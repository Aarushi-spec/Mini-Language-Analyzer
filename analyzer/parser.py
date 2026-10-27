
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.errors = []

    def current(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def advance(self):
        token = self.current()
        if token is not None:
            self.position += 1
        return token

    def check(self, token_type, value=None):
        token = self.current()
        if token is None or token.type != token_type:
            return False
        return value is None or token.value == value

    def expect(self, token_type, value=None):
        token = self.current()

        if self.check(token_type, value):
            return self.advance()

        line = token.line if token else (
            self.tokens[-1].line if self.tokens else 1
        )

        expected = value if value is not None else token_type
        found = repr(token.value) if token else "end of input"

        self.errors.append({
            "line": line,
            "message": f"Expected {expected}, found {found}"
        })

        return None

    def synchronize(self):
        # Recover at the next semicolon to find further errors.
        while self.current() is not None:
            token = self.advance()
            if token.value == ";":
                break

    def parse(self):
        statements = []

        while self.current() is not None:
            old_position = self.position

            statement = self.parse_statement()

            if statement is not None:
                statements.append(statement)

            if self.position == old_position:
                self.advance()

        return statements, self.errors

    def parse_statement(self):
        if self.check("TYPE"):
            return self.parse_declaration()

        if self.check("IDENTIFIER"):
            return self.parse_assignment()

        if self.check("PRINT"):
            return self.parse_print()

        token = self.current()
        line = token.line if token else 1

        self.errors.append({
            "line": line,
            "message": "Invalid statement"
        })

        self.synchronize()
        return None

    def parse_declaration(self):
        type_token = self.advance()
        name_token = self.expect("IDENTIFIER")

        if name_token is None:
            self.synchronize()
            return None

        if self.expect("SEPARATOR", ";") is None:
            self.synchronize()
            return None

        return {
            "kind": "declaration",
            "name": name_token.value,
            "data_type": type_token.value,
            "line": type_token.line
        }

    def parse_assignment(self):
        name_token = self.advance()

        if self.expect("OPERATOR", "=") is None:
            self.synchronize()
            return None

        expression = self.parse_expression()

        if expression is None:
            self.synchronize()
            return None

        if self.expect("SEPARATOR", ";") is None:
            self.synchronize()
            return None

        return {
            "kind": "assignment",
            "name": name_token.value,
            "expression": expression,
            "line": name_token.line
        }

    def parse_print(self):
        print_token = self.advance()

        if self.expect("SEPARATOR", "(") is None:
            self.synchronize()
            return None

        expression = self.parse_expression()

        if expression is None:
            self.synchronize()
            return None

        if self.expect("SEPARATOR", ")") is None:
            self.synchronize()
            return None

        if self.expect("SEPARATOR", ";") is None:
            self.synchronize()
            return None

        return {
            "kind": "print",
            "expression": expression,
            "line": print_token.line
        }

    def parse_expression(self):
        return self.parse_additive()

    def parse_additive(self):
        expression = self.parse_multiplicative()

        while expression is not None and (
            self.check("OPERATOR", "+")
            or self.check("OPERATOR", "-")
        ):
            operator = self.advance()
            right = self.parse_multiplicative()

            if right is None:
                return None

            expression = {
                "kind": "binary",
                "operator": operator.value,
                "left": expression,
                "right": right,
                "line": operator.line
            }

        return expression

    def parse_multiplicative(self):
        expression = self.parse_primary()

        while expression is not None and (
            self.check("OPERATOR", "*")
            or self.check("OPERATOR", "/")
            or self.check("OPERATOR", "%")
        ):
            operator = self.advance()
            right = self.parse_primary()

            if right is None:
                return None

            expression = {
                "kind": "binary",
                "operator": operator.value,
                "left": expression,
                "right": right,
                "line": operator.line
            }

        return expression

    def parse_primary(self):
        token = self.current()

        if token is None:
            self.errors.append({
                "line": self.tokens[-1].line if self.tokens else 1,
                "message": "Expected an expression"
            })
            return None

        if token.type in (
            "INT_LITERAL",
            "FLOAT_LITERAL",
            "STRING_LITERAL",
            "BOOLEAN"
        ):
            self.advance()
            return {
                "kind": "literal",
                "value": token.value,
                "token_type": token.type,
                "line": token.line
            }

        if token.type == "IDENTIFIER":
            self.advance()
            return {
                "kind": "variable",
                "name": token.value,
                "line": token.line
            }

        if self.check("SEPARATOR", "("):
            self.advance()
            expression = self.parse_expression()

            if self.expect("SEPARATOR", ")") is None:
                return None

            return expression

        self.errors.append({
            "line": token.line,
            "message": f"Expected an expression, found {token.value!r}"
        })

        self.advance()
        return None
