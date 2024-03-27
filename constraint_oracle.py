from ast import Tuple
from db.db_connector import connect_to_mysql, load_db_config, logger

import operator

# Mapping from operator symbols to corresponding functions
operator_mapping = {
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le,
    '==': operator.eq,
    '<>': operator.ne
}

class ConstraintOracle:
    def __init__(self):
        config = load_db_config()
        self.db_connection = connect_to_mysql(config)
        if self.db_connection is None:
            logger.error("Failed to connect to the database.")
            raise ConnectionError("Failed to establish a database connection.")
        self.constraints = self.fetch_all_table_constraints()
        self.constraints_op = self.constraints[0]
        self.constraints_val = self.constraints[1]
        self.db_connection.close() 
    
    def __del__(self):
        self.db_connection.close()

    def fetch_all_table_constraints(self):
        """
        Fetch the check constraints for all tables.
        """
        query = """
        SELECT CHECK_CLAUSE FROM information_schema.check_constraints
        """
        cursor = self.db_connection.cursor()
        cursor.execute(query)
        constraint = cursor.fetchall()
        sep_const= constraint[0][0].split(' ')
        operator = sep_const[1]
        check_value = sep_const[2].split(')')[0]
        return operator, check_value
    
    def check_constraint(self, mutated_value) -> bool:

        #first method
        """
        result = eval(f'{mutated_value} {oracle.constraints_op} {oracle.constraints_val}')
        print(result)
        """

        result = operator_mapping.get(self.constraints_op)(mutated_value, int(self.constraints_val))
        print(mutated_value, self.constraints_op, self.constraints_val)
        return result






oracle = ConstraintOracle()
print(oracle.constraints_op, oracle.constraints_val)
oracle.check_constraint(20)
