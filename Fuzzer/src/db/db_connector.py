# db_connector.py
import logging
import os
import time

import mysql.connector

# Setup logger
logger = logging.getLogger("DBLogger")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler for persistent logging
log_file_path = os.path.join(
    os.path.dirname(__file__), "..", "logs", "database-connection-errors.log"
)
file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def log_plain_message(logger, message):
    """
    Logs a plain message without additional info like timestamps and logger names.
    """
    # Save the original formatters
    original_formatters = []
    for handler in logger.handlers:
        original_formatters.append(handler.formatter)
        handler.setFormatter(logging.Formatter("%(message)s"))

    # Log the plain message
    logger.info(message)

    # Restore the original formatters
    for handler, formatter in zip(logger.handlers, original_formatters):
        handler.setFormatter(formatter)


def load_db_config(config_filename="db_config.json"):
    try:
        """Load database configuration from environment variables."""
        config = {
            "host": os.getenv("HOST"),
            "user": os.getenv("USER"),
            "password": os.getenv("PASSWORD"),
            "database": os.getenv("DATABASE"),
        }
        return config
    except FileNotFoundError as e:
        logger.error(f"Failed to load database configuration: {e}")
        return None


def connect_to_mysql(config, attempts=3, delay=2):
    attempt = 1
    # Implement a reconnection routine
    while attempt < attempts + 1:
        try:
            return mysql.connector.connect(**config)
        except (mysql.connector.Error, IOError) as err:
            if attempts is attempt:
                # Attempts to reconnect failed; returning None
                logger.info("Failed to connect, exiting without a connection: %s", err)
                return None
            logger.info(
                "Connection failed: %s. Retrying (%d/%d)...",
                err,
                attempt,
                attempts - 1,
            )
            # progressive reconnect delay
            time.sleep(delay**attempt)
            attempt += 1
    return None
