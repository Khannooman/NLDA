from typing import Dict
from sqlalchemy.engine import URL
import logging

logger = logging.getLogger(__name__)

class OracleWrapper:
    """Wrapper for Oracle."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for Oracle."""
        return URL.create(
            drivername="oracle+cx_oracle",
            username=self.connection_config["username"],
            password=self.connection_config["password"],
            host=self.connection_config["host"],
            port=self.connection_config.get("port", 1521),
            database=self.connection_config["service_name"]  # Use service_name instead of database
        )