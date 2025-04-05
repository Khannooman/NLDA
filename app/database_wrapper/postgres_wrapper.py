from typing import Dict
from sqlalchemy.engine import URL
from app.database_wrapper.base_wrapper import DatabaseWrapper, DatabaseConnectionError
import logging

logger = logging.getLogger(__name__)

class PostgreSQLWrapper(DatabaseWrapper):
    """Wrapper for PostgreSQL."""

    def default_schema(self) -> str:
        """Returns the default schema for PostgreSQL."""
        return "public"
    
    def _create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for postgreSQL."""
        return URL.create(
            "postgresql+psycopg2",
            username=self.connection_config["username"],
            password=self.connection_config["password"],
            host=self.connection_config["host"],
            port=self.connection_config.get("port", 5432),
            database=self.connection_config["database"]
        )