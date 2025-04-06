from typing import Dict
from sqlalchemy.engine import URL
from app.database_wrapper.database_handler import DatabaseHandler
import logging

logger = logging.getLogger(__name__)

class PostgreSQLWrapper:
    """Wrapper for PostgreSQL."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for postgreSQL."""
        return URL.create(
            "postgresql+psycopg2",
            username=self.connection_config["username"],
            password=self.connection_config["password"],
            host=self.connection_config["host"],
            port=self.connection_config.get("port", 5432),
            database=self.connection_config["database"]
        )