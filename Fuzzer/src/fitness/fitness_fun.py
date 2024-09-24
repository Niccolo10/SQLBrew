import logging
import re
import time

from constraint_oracle import ConstraintOracle, is_number
from fitness.base_ff_classes.base_ff import base_ff
from Levenshtein import distance as levenshtein_distance
from mysql.connector import Error as MySQLError

bug_count = 0
current_cycle = 0


class fitness_fun(base_ff):
    def __init__(self):
        super().__init__()
        self.oracle = ConstraintOracle()
        self.default_fitness = 10000

        # Weights for the fitness components
        self.execution_time_weight = 4.0
        self.error_weight = 2.0
        self.constraint_weight = 2.0
        self.proximity_weight = 5.0

    def evaluate(self, ind, **kwargs):
        # Evaluate the individual's fitness based

        global current_cycle
        global bug_count

        cnx = kwargs.get("cnx")
        cursor = kwargs.get("cursor")
        logger = kwargs.get("logger", logging.getLogger())
        cycle_number = kwargs.get("cycle_number")
        if current_cycle != cycle_number:
            current_cycle = cycle_number
            bug_count = 0

        # Initialization
        phenotype = str(ind.phenotype)
        mutated_value = self.extract_value(phenotype)

        error_code = None
        rows_affected = 0
        passed = False
        execution_time = 0
        error_diversity = 0
        constraint_trigger = 0
        proximity = 0

        start_time = time.time()

        try:
            cursor.execute(phenotype)
            cnx.commit()
            passed = True
            rows_affected = cursor.rowcount
        except MySQLError as e:
            error_code = e.errno
            #print(f"Error executing query: {phenotype}. Error: {error_code}")
            # Check for syntax errors (error code 1064)
            if error_code == 1064:
                return self.default_fitness

            # Check for constraint violations (error code 3819)
            if error_code == 3819:
                constraint_trigger = 1
            elif error_code not in [1264, 1366, 1406]:
                error_diversity = 1

        execution_time = time.time() - start_time

        if passed:
            try:
                if "UPDATE" in phenotype:
                    cursor.execute(phenotype.replace("id = 1", "id = 2"))
                else:
                    cursor.execute(phenotype)
                cnx.commit()
                logger.warning(f"\nUNIQUE bug found with query: {phenotype}")
            except MySQLError:
                pass

        oracle_result = self.oracle.evaluate_value_against_constraints(
            "c1", mutated_value
        )
        if oracle_result is None:
            return self.default_fitness

        constraint_value = (
            self.oracle.constraints[0]["value"] if self.oracle.constraints else None
        )

        try:
            if mutated_value is None:
                return self.default_fitness

            db_constraint_error = error_code == 3819

            if oracle_result[0][0] and db_constraint_error and bug_count < 15:
                logger.warning(f"Potential bug found with query: {phenotype}")
                bug_count += 1
            elif (
                not oracle_result[0][0]
                and not db_constraint_error
                and rows_affected > 0
                and bug_count < 15
            ):
                logger.warning(f"Potential bug found with query: {phenotype}")
                bug_count += 1

        except ValueError:
            return self.default_fitness

        proximity = self.calculate_distance(mutated_value, constraint_value)

        # Final fitness calculation using the weighted formula
        fitness = self.calculate_final_fitness(
            proximity, error_diversity, constraint_trigger, execution_time
        )

        return fitness

    def extract_value(self, phenotype):
        # Extract the mutated value from the phenotype
        pattern = r"\(\((.*?)\)\)"
        match = re.search(pattern, phenotype)
        if match:
            return match.group(1)
        return None

    def calculate_distance(self, value, constraint_value):
        # Calculate the distance between the mutated value and the constraint value
        try:
            if is_number(value) and is_number(constraint_value):
                distance = abs(float(value) - float(constraint_value))
            else:
                distance = levenshtein_distance(str(value), str(constraint_value))
            #print(f"Distance: {distance}")
            return distance
        except ValueError:
            return self.default_fitness

    def calculate_final_fitness(
        self, proximity, error_diversity, constraint_trigger, execution_time
    ):
        # Combine all components into a final fitness score using the weighted formula
        fitness = (
            self.proximity_weight * proximity
            + self.error_weight * error_diversity
            + self.constraint_weight * constraint_trigger
            + self.execution_time_weight / (1 + execution_time)
        )
        #print(f"Fitness: {fitness}")
        return fitness
