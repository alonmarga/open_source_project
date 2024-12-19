from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@postgres:5432/mydatabase")

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

def query(sql: str, parameters: dict = None, fetchone: bool = False):
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
        result = conn.execute(sql, parameters or {})
        if fetchone:
            row = result.fetchone()
            return dict(row) if row else None
        return [dict(row) for row in result.fetchall()]