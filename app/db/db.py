from .base import Base
from .connection import engine

class Database:
    def __init__(self):
        self.engine = engine
        self.Base = Base

    def init_db(self):
        """Initialize the database by creating tables."""
        self.Base.metadata.create_all(self.engine)

    def drop_db(self):
        """Drop all tables."""
        self.Base.metadata.drop_all(self.engine)

db = Database()
