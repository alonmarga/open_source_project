from sqlalchemy import create_engine
from contextlib import contextmanager
import os
from sqlalchemy.sql import text
from dotenv import load_dotenv
from psycopg2.extras import execute_values


load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

# Create the database engine
engine = create_engine(DATABASE_URL)

@contextmanager
def get_connection():
    """
    Context manager to get a raw database connection.
    """
    connection = engine.connect()
    try:
        yield connection
    finally:
        connection.close()



def query_db(sql: str, parameters: dict = None, fetchone: bool = False):
    """
    Helper function to execute a SQL query.

    Args:
        sql (str): The SQL query string.
        parameters (dict): The bind parameters for the query.
        fetchone (bool): Whether to fetch one row or all rows.

    Returns:
        list | dict: Query results as a list of dictionaries or a single dictionary.
    """
    with get_connection() as conn:
        result = conn.execute(text(sql), parameters or {})
        if fetchone:
            row = result.fetchone()
            return dict(row._mapping) if row else None
        return [dict(row._mapping) for row in result.fetchall()]


def insert_db(sql: str, parameters: dict = None, returning: bool = False):
    """
    Helper function to execute an INSERT, UPDATE, or DELETE SQL query.

    Args:
        sql (str): The SQL query string.
        parameters (dict): The bind parameters for the query.
        returning (bool): Whether to fetch and return the result of a RETURNING clause.

    Returns:
        dict | None: If `returning` is True, returns the first row as a dictionary. Otherwise, returns None.
    """
    with get_connection() as conn:
        result = conn.execute(text(sql), parameters or {})
        conn.commit()  # Commit the transaction

        if returning:
            row = result.fetchone()
            return dict(row._mapping) if row else None
        return None

def update_db(sql: str, parameters: dict = None):
    """
    Helper function to execute an UPDATE SQL query.

    Args:
        sql (str): The SQL query string.
        parameters (dict): The bind parameters for the query.

    Returns:
        int: Number of rows updated.
    """
    with get_connection() as conn:
        result = conn.execute(text(sql), parameters or {})
        conn.commit()  # Commit the transaction
        return result.rowcount  # Return the number of rows updated


