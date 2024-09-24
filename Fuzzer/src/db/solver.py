from typing import Any, Dict, List, Tuple, Union  # noqa: F401

from isla.solver import GrammarFuzzer, ISLaSolver, Mutator
from isla.type_defs import Grammar

# from tree import display_tree  # noqa: F401


class TableGrammar:
    def __init__(self) -> None:
        self.GRAMMAR: Grammar = {
            "<start>": [
                "CREATE TABLE <table-name> (id INT AUTO_INCREMENT PRIMARY KEY , <column-and-constraints>);",
            ],
            "<table-name>": ["t1"],
            "<column-and-constraints>": ["<column-name> <data-type>"],
            "<column-name>": ["c1"],
            "<data-type>": [
                "<INT-route>",
                "<VARCHAR-route>",
                "<FLOAT-route>",
            ],
            "<INT-route>": [
                "INT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT <constraint-name> CHECK (<generic-check>)"
            ],
            "<VARCHAR-route>": [
                "VARCHAR(255) UNIQUE COLLATE utf8mb4_bin, CONSTRAINT <constraint-name> CHECK (<generic-check>)"
            ],
            "<FLOAT-route>": [
                "FLOAT UNIQUE COLLATE utf8mb4_bin, CONSTRAINT <constraint-name> CHECK (<generic-check>)"
            ],
            "<constraint-name>": ["v1"],
            ("<generic-check>"): ["<only-operator>", "<operator_math>"],
            "<only-operator>": ["c1 <operator> <value>"],
            "<operator_math>": ["c1 <operator> <math-function> <value>"],
            "<operator>": [
                "=",
                ">",
                "<",
                "<=",
                ">=",
                "!=",
                "LIKE",
            ],
            "<math-function>": [
                "ABS",
                "ACOS",
                "COS",
                "EXP",
                "LOG",
                "SIN",
                "SQRT",
                "TAN",
                "CEIL",
                "FLOOR",
                "ASIN",
                "ATAN",
                "DEGREES",
                "RADIANS",
                "ROUND",
                "SIGN",
                "ASCII",
                "BIN",
                "BIT_LENGTH",
                "CHAR_LENGTH",
                "LENGTH",
                "LOWER",
                "UPPER",
            ],
            "<value>": [
                "(<is_negative><numeric-value>)",
                "('<string-value>')",
                "<boolean-value>",
                "<mixed-value>",
            ],
            "<numeric-value>": ["<digits>", "<digits>.<digits>"],
            "<string-value>": ["<strings>"],
            "<boolean-value>": ["<boolean>"],
            "<mixed-value>": ["('<mixs>')"],
            "<boolean>": ["(TRUE)", "(FALSE)"],
            "<strings>": ["<string>", "<string><strings>", "<string><strings><string>"],
            "<string>": list(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ "
            ),
            "<digits>": ["<digit><digits>", "<digit>", "<digit><digits><digit>"],
            "<digit>": list("0123456789"),
            "<mixs>": ["<mix>", "<mix><mixs>", "<mix><mixs><mix>"],
            "<mix>": list(
                "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\f\v"
            ),
            "<is_negative>": ["-", ""],
        }
        # DEFAULT NULL values
        # self.constraints = """  <math-function> = <placeholder> """

        self.mutator = Mutator(self.GRAMMAR, min_mutations=2, max_mutations=5)

        self.fuzzer = GrammarFuzzer(self.GRAMMAR)

    def solve(self, max_free_instantiations=10, max_smt_instantiations=10):
        solver = ISLaSolver(
            grammar=self.GRAMMAR,
            # formula=self.constraints,
            max_number_free_instantiations=max_free_instantiations,
            max_number_smt_instantiations=max_smt_instantiations,
            debug=True,
        )

        try:
            solution = solver.solve()

        except StopIteration:
            pass  # Handle the case when no more unique solutions can be generated
        return solution


"""
table = TableGrammar()
solutions = []

for i in range(20):
    solutions = table.solve()
    print(str(solutions))
"""
