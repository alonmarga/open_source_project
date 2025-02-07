from sqlalchemy import create_engine
from contextlib import contextmanager
import os
from sqlalchemy.sql import text
from dotenv import load_dotenv
from psycopg2.extras import execute_values
import psycopg2

load_dotenv()

DATABASE_URL = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@postgres:5432/{os.environ.get('POSTGRES_DB')}"

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


@contextmanager
def get_psycopg2_connection():
    """
    Context manager to get a psycopg2 connection for batch operations.
    """

    connection = psycopg2.connect(DATABASE_URL)
    try:
        yield connection
    finally:
        connection.close()


def batch_insert(table_name: str, columns: list, values: list, page_size: int = 1000):
    """
    Helper function to perform batch insert operations.

    Args:
        table_name (str): Name of the table to insert into
        columns (list): List of column names
        values (list): List of tuples containing values to insert
        page_size (int): Number of rows to insert in each batch

    Returns:
        int: Total number of rows inserted
    """
    insert_query = f"""
        INSERT INTO {table_name} ({','.join(columns)})
        VALUES %s
    """
    total_rows = 0

    with get_psycopg2_connection() as conn:
        with conn.cursor() as cur:
            try:
                execute_values(cur, insert_query, values, page_size=page_size)
                conn.commit()
                total_rows = cur.rowcount
            except Exception as e:
                conn.rollback()
                raise Exception(f"Batch insert failed: {str(e)}")

    return total_rows