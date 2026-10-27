
class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = []
        self.symbols = {}
        self.errors = []

    def error(self, line, message):
        self.errors.append({
            "line": line,
            "message": message
        })

    def analyze(self, statements):
        for statement in statements:
            kind = statement["kind"]
            line = statement["line"]

            if kind == "declaration":
                name = statement["name"]
                data_type = statement["data_type"]

                if name in self.symbols:
                    self.error(
                        line,
                        f"Duplicate declaration of variable '{name}'"
                    )
                else:
                    symbol = {
                        "name": name,
                        "data_type": data_type,
                        "scope": "global",
                        "declaration_line": line,
                        "initialized": False
                    }

                    self.symbols[name] = symbol
                    self.symbol_table.append(symbol.copy())

            elif kind == "assignment":
                name = statement["name"]

                if name not in self.symbols:
                    self.error(
                        line,
                        f"Variable '{name}' used without declaration"
                    )
                    continue

                expression_type = self.get_expression_type(
                    statement["expression"]
                )

                if expression_type is None:
                    continue

                target_type = self.symbols[name]["data_type"]

                if not self.is_compatible(
                    target_type, expression_type
                ):
                    self.error(
                        line,
                        f"Type mismatch: cannot assign "
                        f"'{expression_type}' to '{target_type}' "
                        f"variable '{name}'"
                    )
                else:
                    self.symbols[name]["initialized"] = True

            elif kind == "print":
                self.get_expression_type(statement["expression"])

        return self.symbol_table, self.errors

    def is_compatible(self, target_type, source_type):
        if target_type == source_type:
            return True

        # Allow an integer value in a float variable.
        if target_type == "float" and source_type == "int":
            return True

        return False

    def get_expression_type(self, expression):
        kind = expression["kind"]
        line = expression["line"]

        if kind == "literal":
            token_type = expression["token_type"]

            if token_type == "INT_LITERAL":
                return "int"

            if token_type == "FLOAT_LITERAL":
                return "float"

            if token_type == "STRING_LITERAL":
                return "string"

            if token_type == "BOOLEAN":
                return "bool"

        if kind == "variable":
            name = expression["name"]

            if name not in self.symbols:
                self.error(
                    line,
                    f"Variable '{name}' used without declaration"
                )
                return None

            if not self.symbols[name]["initialized"]:
                self.error(
                    line,
                    f"Variable '{name}' may be used before initialization"
                )

            return self.symbols[name]["data_type"]

        if kind == "binary":
            left_type = self.get_expression_type(expression["left"])
            right_type = self.get_expression_type(expression["right"])
            operator = expression["operator"]

            if left_type is None or right_type is None:
                return None

            if operator == "+" and (
                left_type == "string" and right_type == "string"
            ):
                return "string"

            numeric_types = {"int", "float"}

            if (
                left_type not in numeric_types
                or right_type not in numeric_types
            ):
                self.error(
                    line,
                    f"Operator '{operator}' requires numeric operands"
                )
                return None

            if operator == "%" and (
                left_type != "int" or right_type != "int"
            ):
                self.error(
                    line,
                    "Operator '%' requires integer operands"
                )
                return None

            if (
                operator == "/"
                and expression["right"]["kind"] == "literal"
                and expression["right"]["value"] in ("0", "0.0")
            ):
                self.error(line, "Division by zero")
                return None

            if left_type == "float" or right_type == "float":
                return "float"

            return "int"

        return None
