from typing import Dict
from sqlalchemy.engine import URL
from app.database_wrapper.base_wrapper import DatabaseWrapper, DatabaseConnectionError
import logging

logger = logging.getLogger(__name__)

class MySQLWrapper(DatabaseWrapper):
    """Wrapper for MySQL."""

    def default_schema(self) -> str:
        """Returns the default schema for MySQL (database name)."""
        return self.connection_config['database']
    
    def _create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for MySQL."""
        return URL.create(
            "MySQL+mysqlconnector",
            username=self.connection_config["username"],
            password=self.connection_config["password"],
            host=self.connection_config["host"],
            port=self.connection_config.get("port", 3306),
            database=self.connection_config["database"],
        )