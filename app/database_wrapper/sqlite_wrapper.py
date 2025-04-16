from typing import Dict
from sqlalchemy.engine import URL
import logging

logger = logging.getLogger(__name__)

class SQLiteWrapper:
    """Wrapper for SQLite."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for SQLite."""
        database_path = self.connection_config["database"]  # Path to SQLite file (e.g., /path/to/database.db)
        return URL.create(
            drivername="sqlite",
            database=database_path
        )