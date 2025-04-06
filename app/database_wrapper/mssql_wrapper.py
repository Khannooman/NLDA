from typing import Dict
from sqlalchemy.engine import URL
import logging

logger = logging.getLogger(__name__)

class MSSQLWrapper:
    """Wrapper for MSSQL."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for MSSQL."""
        return URL.create(
            "MSSQL+MSSQLconnector",
            username=self.connection_config["username"],
            password=self.connection_config["password"],
            host=self.connection_config["host"],
            port=self.connection_config.get("port", 1433),
            database=self.connection_config["database"],
        )