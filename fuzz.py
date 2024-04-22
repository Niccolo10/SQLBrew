from mysql.connector import Error

from db.db_connector import connect_to_mysql, load_db_config, logger

# Import your grammar and solver classes
from grammar.solver import OperationGrammar, TableGrammar


class DBFuzzer:
    def __init__(self):
        self.config = load_db_config()
        # self.oracle = co.ConstraintOracle()
        self.cnx = None
        self.cursor = None
        if self.config:
            self.connect_to_db()
        self.table_grammar = TableGrammar()
        self.operation_grammar = OperationGrammar()

    def connect_to_db(self):
        try:
            self.cnx = connect_to_mysql(self.config)
            self.cursor = self.cnx.cursor()
            logger.info("Database connection established.")
        except Error as e:
            logger.critical(f"Failed to connect to the database: {e}")

    def reset_db(self):
        reset_query = "DROP TABLE IF EXISTS t1;"
        try:
            self.cursor.execute(reset_query)
            self.cnx.commit()
            logger.info("Database reset successfully.")
        except Error as e:
            logger.error(f"Failed to reset the database: {e}")
        pass

    def create_table(self):
        create_table_sql = str(self.table_grammar.solve())
        print(create_table_sql)
        try:
            self.cursor.execute(create_table_sql)
            self.cnx.commit()
            logger.info("Table created successfully.")
        except Error as e:
            logger.error(f"Failed to create table: {e}")
            self.create_table()

    def perform_operations(self):
        solutions = self.operation_grammar.solve()
        for solution in solutions:
            operation_sql = str(
                solution
            )  # Assuming str(solution) returns the SQL statement
            mutated_value = operation_sql.split()[-1].strip(");").strip("(")
            # Example to extract mutated value
            # answer = self.oracle.check_constraint(mutated_value)
            answer = True  # Placeholder for the oracle evaluation
            try:
                print(operation_sql)
                self.cursor.execute(operation_sql)
                self.cnx.commit()
                logger.info(f"Executed operation - Oracle evaluation: {answer}")
                if not answer:
                    logger.info(
                        f"Mutated value: {mutated_value} did not trigger the constraint as expected."
                    )
            except Error as e:
                logger.error(
                    f"Error during operation: {e} - Oracle evaluation: {answer}"
                )
                if answer:
                    logger.info(
                        f"Mutated value: {mutated_value} should have triggered the constraint."
                    )

    def run_fuzzing_cycle(self):
        if self.cnx is not None:
            self.reset_db()
            self.create_table()
            self.perform_operations()
            self.cursor.close()
            self.cnx.close()
        else:
            logger.error("No database connection is available.")


# Usage
if __name__ == "__main__":
    fuzzer = DBFuzzer()
    fuzzer.run_fuzzing_cycle()
