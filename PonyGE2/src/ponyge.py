import sys

from algorithm.parameters import params, set_params
from mysql.connector import Error
from stats.stats import get_stats

from db.db_connector import connect_to_mysql, load_db_config, logger
from db.solver import TableGrammar


class DBFuzzer:
    def __init__(self):
        self.config = load_db_config()
        # self.oracle = co.ConstraintOracle()
        self.cnx = None
        self.cursor = None
        if self.config:
            self.connect_to_db()
        self.table_grammar = TableGrammar()

    def connect_to_db(self):
        try:
            self.cnx = connect_to_mysql(self.config)
            self.cursor = self.cnx.cursor()
            logger.info("Database connection established.")
        except Error as e:
            logger.critical(f"Failed to connect to the database: {e}")

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

    def reset_db(self):
        reset_query = "DROP TABLE IF EXISTS t1;"
        try:
            self.cursor.execute(reset_query)
            self.cnx.commit()
            logger.info("Database reset successfully.")
        except Error as e:
            logger.error(f"Failed to reset the database: {e}")
        pass

    def run_fuzzing_cycle(self):
        if self.cnx is not None:
            self.reset_db()
            self.create_table()
            self.perform_operations()
            self.cursor.close()
            self.cnx.close()
        else:
            logger.error("No database connection is available.")

    def perform_operations(self):
        set_params(sys.argv[1:])
        individuals = params["SEARCH_LOOP"](self.cnx, self.cursor, logger)

        get_stats(individuals, end=True)


def main():
    fuzzer = DBFuzzer()
    fuzzer.run_fuzzing_cycle()


if __name__ == "__main__":
    main()
