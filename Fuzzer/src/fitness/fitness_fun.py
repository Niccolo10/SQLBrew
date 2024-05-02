import re

from fitness.base_ff_classes.base_ff import base_ff


class fitness_fun(base_ff):
    """
    Fitness function to evaluate how close a numeric value (extracted from SQL query) is to zero.
    It inherits from the base fitness function class. The fitness function aims to minimize the
    absolute value of the number, encouraging values close to but not exactly zero.
    """

    def __init__(self):
        super().__init__()
        # You might want to set default fitness to a high value if closer to zero is better.
        self.default_fitness = float(
            "inf"
        )  # High default fitness penalizes non-ideal conditions.

    def evaluate(self, ind, **kwargs):
        """
        Evaluate the individual's fitness based on how close the extracted value from the phenotype
        SQL query is to zero but not exactly zero.

        :param ind: An individual whose phenotype is a SQL string.
        :param kwargs: Optional arguments, not used here.
        :return: The fitness of the evaluated individual.
        """
        cnx = kwargs.get("cnx")
        cursor = kwargs.get("cursor")
        logger = kwargs.get("logger")

        phenotype = str(ind.phenotype)
        value = self.extract_value(phenotype)

        try:
            cursor.execute(phenotype)
            cnx.commit()
            # logger.info("Query executed successfully: %s", phenotype)
        except Exception:
            # logger.error("Error executing query: %s. Error: %s", phenotype, str(e))
            print(ind.phenotype, value)
        if value is None:
            return (
                self.default_fitness
            )  # Return default if no value is extracted or if it's not numeric

        # Convert value to a float and calculate fitness
        try:
            numeric_value = float(value)
            if numeric_value == 0:
                return self.default_fitness  # Penalize exactly zero
            fitness = abs(
                numeric_value
            )  # Fitness is the absolute value, lower is better
        except ValueError:
            return self.default_fitness  # Penalize non-numeric values

        return fitness

    def extract_value(self, phenotype):
        """
        Extracts the numeric value from SQL queries using a regex.
        Assumes the value is enclosed in parentheses followed by a semicolon.

        :param phenotype: The SQL query string.
        :return: The extracted value or None if no pattern matches or the value isn't suitable.
        """
        pattern = r"\(\((.*?)\)\)"
        match = re.search(pattern, phenotype)
        if match:
            return match.group(1)
        return None
