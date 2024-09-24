import decimal
import math
import operator
import re

from db.db_connector import connect_to_mysql, load_db_config


def like(a, b):
    # Convert SQL LIKE pattern to regex pattern
    a = str(a)
    b = str(b)
    regex_pattern = "^" + re.escape(b).replace("%", ".*").replace("_", ".") + "$"
    result = bool(re.match(regex_pattern, a))

    return result


def is_number(s):
    pattern = r"[+-]?\d+(\.\d+)?"
    return bool(re.fullmatch(pattern, s))


def starts_with_number(s):
    pattern = r"[+-]?\d+"
    match = re.match(pattern, s)
    if match:
        return True, match.group()
    else:
        return False, None


def not_like(a, b):
    # Convert SQL LIKE pattern to regex pattern
    regex_pattern = re.escape(b).replace("%", ".*").replace("_", ".")
    return not bool(re.match(regex_pattern, a))


# Mapping from operator symbols to corresponding functions
operator_mapping = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "=": operator.eq,
    "!=": operator.ne,
    "<>": operator.ne,
    "like": like,
    "not": not_like,  # not like
}

sql_functions = {
    "abs": abs,
    "cos": math.cos,
    "exp": math.exp,
    "log": math.log,
    "sin": math.sin,
    "sqrt": math.sqrt,
    "tan": math.tan,
    "ceiling": math.ceil,
    "floor": math.floor,
    "asin": math.asin,
    "atan": math.atan,
    "degrees": math.degrees,
    "radians": math.radians,
    "round": round,
    "sign": math.copysign,
    "ascii": ord,
    # "bin": bin,
    "bit_length": lambda x: x.bit_length(),
    "char_length": len,
    "length": len,
    "lower": str.lower,
    "upper": str.upper,
    # Add others as necessary
}

char_only_functions = ["bit_length", "char_length", "length", "lower", "upper"]


class ConstraintOracle:
    def __init__(self):
        config = load_db_config()
        self.db_connection = connect_to_mysql(config)
        if self.db_connection is None:
            raise ConnectionError("Failed to establish a database connection.")

        self.constraints = self.fetch_all_table_constraints()
        self.isutf8mb4 = False
        self.constraints[0]["value"] = self.clean_string(self.constraints[0]["value"])
        if self.constraints[0]["value"] == "true":
            self.constraints[0]["value"] = 1
        elif self.constraints[0]["value"] == "false":
            self.constraints[0]["value"] = 0
        self.pre_evaluate_constraints()
        self.db_connection.close()

    def __del__(self):
        self.db_connection.close()

    def fetch_all_table_constraints(self):
        """
        Fetch the check constraints for all tables.
        """
        query = """ SELECT 
            tc.TABLE_NAME,
            cc.CONSTRAINT_NAME,
            cc.CHECK_CLAUSE,
            c.COLUMN_NAME,
            c.DATA_TYPE
        FROM 
            information_schema.TABLE_CONSTRAINTS tc
        JOIN 
            information_schema.CHECK_CONSTRAINTS cc ON tc.CONSTRAINT_NAME = cc.CONSTRAINT_NAME 
                AND tc.CONSTRAINT_SCHEMA = cc.CONSTRAINT_SCHEMA
        JOIN 
            information_schema.COLUMNS c ON tc.TABLE_SCHEMA = c.TABLE_SCHEMA 
                AND tc.TABLE_NAME = c.TABLE_NAME 
        WHERE 
            tc.TABLE_SCHEMA = (SELECT DATABASE()) 
            AND tc.TABLE_NAME = 't1' 
            AND tc.CONSTRAINT_TYPE = 'CHECK'
            AND c.COLUMN_NAME = 'c1';   
        """
        cursor = self.db_connection.cursor()
        cursor.execute(query)
        constraint = cursor.fetchall()
        # print(constraint)
        constraints_info = []
        for row in constraint:
            column_name, operator, math_ops, value = self.parse_check_clause(row[2])
            char_flag = math_ops in char_only_functions
            constraints_info.append(
                {
                    "table_name": row[0],
                    "constraint_name": row[1],
                    "check_clause": row[2],
                    "parsed_column_name": column_name,
                    "operator": operator,
                    "math_ops": math_ops,
                    "value": value,
                    "data_type": row[4],
                    "char_flag": char_flag,
                }
            )

        return constraints_info

    def parse_check_clause(self, check_clause):
        # print(f"Check clause: {check_clause}")
        match = re.search(
            r"`(\w+)`\s*(\W+|!=|>=|<=|=|like)\s(-?)*\(([^)]*)\)\)",
            check_clause,
            re.IGNORECASE,
        )
        if match:
            column_name, operator, negative, value = match.groups()
            # print(f"Match: {column_name}, {operator}, , {value}")

            value = "-" + value
            return column_name, operator.strip(), None, value

        match = re.search(r"`(\w+)`\s*(\W+|!=|>=|<=|=|like)\s*(.*)\)", check_clause)
        if match:
            column_name, operator, value = match.groups()
            # Trim whitespace around the operator to ensure correct mapping
            math_ops_match = re.match(r"(\w+)\((.*)\)", value.strip())
            if math_ops_match:
                math_ops, inner_value = math_ops_match.groups()
                return (
                    column_name,
                    operator.strip(),
                    math_ops,
                    inner_value.replace("(", "").replace(")", "").strip("`"),
                )
            else:
                return column_name, operator.strip(), None, value.strip("`")
        # print("No match while parsing check clause.")
        return None, None, None, None

    def evaluate_sql_function(self, sql_function, value):
        """
        Evaluates an SQL function using the database. Returns None if the evaluation fails.
        """
        try:
            query = f"SELECT {sql_function}({value});"
            cursor = self.db_connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()

            if result:
                return result[0]
            return None
        except Exception:
            # print(f"Error evaluating SQL function {sql_function}({value}): {e}")
            return None  # Returning None to signify an error

    def pre_evaluate_constraints(self):
        # Evaluate constraints using SQL queries for supported functions
        for constraint in self.constraints:
            if constraint["math_ops"]:
                # print(f"Math ops: {constraint['math_ops']}, isutf8mb4: {self.isutf8mb4}")
                try:
                    # Fetch the value from the database instead of using Python functions
                    evaluated_value = self.evaluate_sql_function(
                        constraint["math_ops"], constraint["value"]
                    )

                    if evaluated_value is not None:
                        constraint["value"] = str(evaluated_value)
                        # print(f"Evaluated value from DB: {evaluated_value}")
                    else:
                        # Handle error where the value could not be evaluated
                        # print(f"Error evaluating SQL function: {constraint['math_ops']}({constraint['value']})")
                        constraint["value"] = None

                except Exception:
                    # print(f"Exception during evaluation: {e}")
                    constraint["value"] = None

    def evaluate_value_against_constraints(self, column_name, value):
        results = []
        for constraint in self.constraints:
            try:
                # Handle NULL values
                # print(f"constraint value: {constraint['value']}, type: {type(constraint['value'])}")
                if constraint["value"] is None:
                    results.append((False, constraint["constraint_name"], "Type error"))
                    continue

                if value is True:
                    value = 1
                elif value is False:
                    value = 0

                # print(f"Value: {value}, type: {type(value)}")
                converted_value, constraint_value = self.convert_values(
                    value, constraint["value"], constraint["data_type"]
                )
                operator_func = operator_mapping.get(constraint["operator"])
                if not operator_func:
                    # print(f"Operator '{constraint['operator']}' is not recognized.")
                    continue

                result = operator_func(converted_value, constraint_value)
                results.append((result, constraint["constraint_name"]))
                # print(f"self.constraints: {self.constraints}, constraint: {constraint}\n" f"Debug: {converted_value} {constraint['operator']} {constraint_value} -> {result} ({type(converted_value)}, {type(constraint_value)})")
            except ValueError:
                # print(f"Type conversion error: {e}")
                results.append((False, constraint["constraint_name"], "Type error"))
        return results

    def convert_values(self, input_value, constraint_value, data_type):
        try:
            if data_type in ["int", "decimal", "float", "double"]:
                return self.convert_numeric_values(
                    input_value, constraint_value, data_type
                )
            elif data_type == "varchar":
                return self.convert_string_values(input_value, constraint_value)
            else:
                raise ValueError("Unsupported data type")
        except ValueError:
            # print(f"Value conversion error: {e}")
            raise

    def convert_numeric_values(self, input_value, constraint_value, data_type):
        try:
            if data_type == "decimal":
                input_value = decimal.Decimal(input_value)
            else:
                input_value = self.convert_to_number(input_value)
                constraint_value = self.convert_to_number(constraint_value)
            return input_value, constraint_value
        except ValueError:
            raise

    def convert_to_number(self, value):
        try:
            # Attempt to convert string to number
            if isinstance(value, str):
                try:
                    return float(value) if "." in value else int(value)
                except ValueError:
                    raise ValueError(
                        "Data truncated for column"
                    )  # Mimic MySQL behavior
            return value
        except ValueError:
            raise ValueError(
                "Data truncated for column"
            )  # Default to 0 for non-convertible values

    def convert_string_values(self, input_value, constraint_value):
        try:
            if is_number(str(input_value)):
                # print("Input value is a number")
                if is_number(str(constraint_value)):
                    input_value = self.convert_to_number(input_value)
                    constraint_value = self.convert_to_number(constraint_value)
                elif starts_with_number(constraint_value)[0]:
                    # print("Constraint value starts with number")
                    input_value = self.convert_to_number(input_value)
                    constraint_value = self.convert_to_number(
                        starts_with_number(constraint_value)[1]
                    )

                for constraint in self.constraints:
                    if constraint["math_ops"] in [
                        "char_length",
                        "length",
                        "bit_length",
                    ]:
                        return input_value, constraint_value
            # Convert both input and constraint values to string for comparison
            input_value = self.convert_to_string(input_value)
            constraint_value = self.convert_to_string(constraint_value)

            return input_value, constraint_value
        except ValueError:
            raise ValueError("String value conversion error")

    def convert_to_string(self, value):
        try:
            return str(value)
        except ValueError:
            raise ValueError("String conversion error")

    def clean_string(self, value):
        if value.startswith("_utf8mb4"):
            value = value.split("'")[1]
            self.isutf8mb4 = True
        # Strip any leading or trailing whitespace
        value = value.strip()
        # Remove any potential escape characters
        return value.replace("\\", "")


# Example usage
oracle = ConstraintOracle()
result = oracle.evaluate_value_against_constraints("c1", 4.7)
# print(result)
