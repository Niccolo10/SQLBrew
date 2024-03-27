from db.db_connector import connect_to_mysql, load_db_config, logger
import random
from mysql.connector import Error
import constraint_oracle as co

add_employee = ("INSERT INTO employees "
               "(name, age) "
               "VALUES (%s, %s)")

# Load the configuration
config = load_db_config()

oracle = co.ConstraintOracle()

if config is not None:
    try:
        cnx = connect_to_mysql(config)
        
        if cnx is not None:
            logger.info("Starting fuzzing operations...")
            cursor = cnx.cursor()

            for i in range(5):
                mutated_value = 17.99999999999999
                data_employee = ('employee{i}', mutated_value)  # Fixed typo in 'employee'
                answer = oracle.check_constraint(mutated_value)

                try:
                    # Attempt to insert new employee
                    cursor.execute(add_employee, data_employee)
                    cnx.commit()

                    # Log insertion info with oracle's evaluation
                    logger.info(f"Inserted new employee with ID: {cursor.lastrowid} - Oracle evaluation: {answer}")
                    if answer == False:
                        logger.info(f"Mutated value: {mutated_value} - Oracle evaluation: {answer}") #BUUUUGGGGGG
                except Error as e:
                    # Log the error and continue with the next iteration
                    logger.error(f"An error occurred during the insertion of the new employee: {e} - Oracle evaluation: {answer}")
                    if answer == True:
                        logger.info(f"Mutated value: {mutated_value} - Oracle evaluation: {answer}") #BUUUUGGGGGG
                    continue

            # Remember to close the cursor and connection after operations
            cursor.close()
            cnx.close()
        else:
            logger.error("Database connection could not be established.")
    except Exception as e:
        logger.critical(f"An unexpected error occurred during fuzzing operations: {e}")
else:
    logger.error("Could not load the database configuration.")
