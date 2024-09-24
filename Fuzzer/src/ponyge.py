import io
import json
import os
import sys

from algorithm.parameters import params, set_params
from mysql.connector import Error
from stats.stats import get_stats

from db.db_connector import connect_to_mysql, load_db_config, log_plain_message, logger
from db.solver import TableGrammar


class DBFuzzer:
    def __init__(self):
        self.config = load_db_config()
        # self.oracle = co.ConstraintOracle()
        self.cnx = None
        self.cursor = None
        self.cycle_number = 1
        if self.config:
            self.connect_to_db()
        self.table_grammar = TableGrammar()

    def connect_to_db(self):
        try:
            self.cnx = connect_to_mysql(self.config)
            self.cursor = self.cnx.cursor()
        except Error as e:
            logger.critical(f"Failed to connect to the database: {e}")

    def create_table(self):
        create_table_sql = str(self.table_grammar.solve())
        log_plain_message(logger, "_____________________________________________\n")
        logger.info(
            f"Cycle {self.cycle_number}: Creating table with SQL: \n\n{create_table_sql}\n"
        )
        try:
            self.cursor.execute(create_table_sql)
            self.cnx.commit()
        except Error as e:
            logger.error(f"Failed to create the table: {e}")
            self.create_table()

    def first_insertion(self):
        insert_query = "INSERT INTO t1 (c1) VALUES (NULL);"
        try:
            self.cursor.execute(insert_query)
            self.cnx.commit()
        except Error as e:
            logger.error(f"Failed to insert a row into the table: {e}")
        try:
            self.cursor.execute(insert_query)
            self.cnx.commit()
        except Error as e:
            logger.error(f"Failed to insert a row into the table: {e}")

    def reset_db(self):
        reset_query = "DROP TABLE IF EXISTS t1;"
        try:
            self.cursor.execute(reset_query)
            self.cnx.commit()
        except Error as e:
            logger.error(f"Failed to reset the database: {e}")
        pass

    def run_fuzzing_cycle(self):
        if self.cnx is not None:
            self.reset_db()
            self.create_table()
            self.first_insertion()
            self.perform_operations()
            self.cursor.close()
            self.cnx.close()
        else:
            logger.error("No database connection is available.")

    def perform_operations(self):
        set_params(sys.argv[1:])

        # Generate individuals without capturing their output
        individuals = params["SEARCH_LOOP"](
            self.cnx, self.cursor, logger, self.cycle_number
        )

        # Prepare to capture only the output from get_stats
        captured_output = io.StringIO()
        original_stdout = sys.stdout  # Save the original stdout

        try:
            sys.stdout = captured_output  # Redirect stdout to the StringIO object
            get_stats(individuals, end=True)  # Capture only the output from get_stats
        finally:
            sys.stdout = original_stdout  # Restore original stdout

        # Get the captured output from get_stats
        stats_output = captured_output.getvalue()

        # Log the captured stats output
        logger.info(f"\nStatistics:\n{stats_output}")

    @staticmethod
    def save_params_to_file(params, filename):
        with open(filename, "w") as file:
            json.dump(params, file, indent=4)

    @staticmethod
    def load_params_from_file(filename):
        with open(filename, "r") as file:
            loaded_params = json.load(file)
        params.update(loaded_params)


def main():
    params_filename = "params.json"

    # Save params to file once if not already done
    if not os.path.exists(params_filename):
        DBFuzzer.save_params_to_file(params, params_filename)
    cycle_number = 1
    while cycle_number > 0:
        try:
            DBFuzzer.load_params_from_file(params_filename)
            fuzzer = DBFuzzer()
            fuzzer.cycle_number = cycle_number
            fuzzer.run_fuzzing_cycle()
            cycle_number += 1
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            continue
        # Optional: Sleep for a while before starting the next cycle


if __name__ == "__main__":
    main()
