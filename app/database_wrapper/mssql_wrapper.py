from typing import Dict
from sqlalchemy.engine import URL
from app.database_wrapper.base_wrapper import DatabaseWrapper, DatabaseConnectionError
import logging

logger = logging.getLogger(__name__)

class MSSQLWrapper(DatabaseWrapper):
    """Wrapper for MSSQL."""

    def default_schema(self) -> str:
        """Returns the default schema for MSSQL."""
        return "dbo"
    
    def _create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for MSSQL."""
        return URL.create(
            "MSSQL+MSSQLconnector",
            username=self.connection_config["username"],
            password=self.connection_config["password"],
            host=self.connection_config["host"],
            port=self.connection_config.get("port", 1433),
            database=self.connection_config["database"],
        )