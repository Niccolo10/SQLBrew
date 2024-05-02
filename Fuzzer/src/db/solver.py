from typing import Any, Dict, List, Tuple, Union  # noqa: F401

from isla.solver import GrammarFuzzer, ISLaSolver, Mutator
from isla.type_defs import Grammar

# from tree import display_tree  # noqa: F401


class TableGrammar:
    def __init__(self) -> None:
        self.GRAMMAR: Grammar = {
            "<start>": [
                "CREATE TABLE <table-name> (id INT AUTO_INCREMENT PRIMARY KEY , <column-and-constraints>);"
            ],
            "<table-name>": ["t1"],
            "<column-and-constraints>": [
                "<column>, CONSTRAINT <constraint-name> CHECK (<check-condition>)",
            ],
            "<column>": ["<column-name> <data-type>"],
            "<column-name>": ["c1"],
            "<data-type>": ["INT", "VARCHAR(255)", "BOOLEAN", "FLOAT"],
            "<constraint-name>": ["v1"],
            "<check-condition>": [
                "c1 " "<operator>" " <value>",
                "c1 " "<operator>" " <function>" " <value>",
                "c1 " "<operator>" " <value> " "AND " "<check-condition>",
            ],
            "<value>": ["(<digits>)", "(<digits>.<digits>)", "(<strings>)"],
            "<strings>": ["<string>", "<string><strings>"],
            "<digits>": ["<digit><digits>", "<digit>"],
            "<operator>": [
                "=",
                ">",
                "<",
                "<=",
                ">=",
                "!=",
            ],
            "<function>": [
                "ABS",
                "ACOS",
                "CHAR_LENGTH",
                "COS",
                "EXP",
                "LOG",
                "MOD",
                "ROUND",
                "SIN",
                "SQRT",
                "TAN",
                "HEX",
                "LENGTH",
                "LIKE",
            ],
            "<digit>": list("0123456789"),
            "<string>": list("abcdefghijklmnopqrstuvwxyz"),
        }

        # self.constraints = """ str.to.int(<digit>) > 5"""

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
# Example usage:
table = TableGrammar()
solutions = []

for i in range(20):
    solutions = table.solve()
    for solution in solutions:
        print((solution))
        # mutated_solution = table.mutate(solution)
        # print(
        #    mutated_solution
        # )  # str(solution) if i want the string -> now is returning DerivationTree / print implicity transform in string
# dot = display_tree(solution)
# dot.render("output_filename", view=True)

operation = OperationGrammar()
solutions = []

for i in range(20):
    solutions = operation.solve()
    for solution in solutions:
        print((solution))
        # mutated_solution = table.mutate(solution)
        # print(
        #    mutated_solution
        # )  # str(solution) if i want the string -> now is returning DerivationTree / print implicity transform in string
"""
