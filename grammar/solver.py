from typing import List, Dict, Union, Any, Tuple
from isla.solver import ISLaSolver
from isla.type_defs import Grammar
from isla.derivation_tree import DerivationTree
from tree import display_tree

fake = DerivationTree( "<start>" )

class TableGrammar:
    def __init__(self) -> None:

        self.GRAMMAR : Grammar = {
            "<start>": ["CREATE TABLE <table-name> (<columns-and-constraints>);"],
            "<table-name>": ["t1"],
            "<columns-and-constraints>": [
                "<column>, CONSTRAINT <constraint-name> CHECK (<check-condition>)",
                "<column>, <column>, CONSTRAINT <constraint-name> CHECK (<compare-two-columns>)"
            ],
            "<column>": ["<column-name> <data-type>"],
            "<column-name>": ["c1", "c2"],
            "<data-type>": ["INT", "VARCHAR(255)", "BOOLEAN", "FLOAT"],
            "<constraint-name>": ["v1"],
            "<check-condition>": ["c1 > <digits>", "CHAR_LENGTH(c1) > <digits>", "c1 LIKE '%@%.%'"],
            "<compare-two-columns>": ["c1 < c2", "c1 > c2", "CHAR_LENGTH(c1) > CHAR_LENGTH(c2)"],
            "<digits>": ["<digit><digits>", "<digit>"],
            "<digit>": list("0123456789")
        }

        self.constraints = ''' str.to.int(<digit>) > 5'''

    def solve(self, max_free_instantiations=10, max_smt_instantiations=10):

        solver = ISLaSolver(
            grammar=self.GRAMMAR,
            #formula=self.constraints,
            max_number_free_instantiations=max_free_instantiations,
            max_number_smt_instantiations=max_smt_instantiations,
            debug=True
        )
        solutions = []
        
        try:
            for _ in range(1):  # Adjust the number of attempts as needed
                solution = solver.solve()
                if solution:
                    solutions.append(solution)
                else:
                    break
        except StopIteration:
            pass  # Handle the case when no more unique solutions can be generated
        return solutions

# Example usage:
table = TableGrammar()
solutions = table.solve()
for solution in solutions:
    print((solution)) # str(solution) if i want the string -> now is returning DerivationTree / print implicity transform in string
    dot = display_tree(solution)
    dot.render('output_filename', view=True)

    #print("ciao")
