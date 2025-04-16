from typing import Dict
from sqlalchemy.engine import URL
import logging

logger = logging.getLogger(__name__)

class SnowflakeWrapper:
    """Wrapper for Snowflake."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for Snowflake."""
        return URL.create(
            drivername="snowflake",
            username=self.connection_config["username"],
            password=self.connection_config["password"],
            host=f"{self.connection_config['account']}.{self.connection_config['region']}.snowflakecomputing.com",
            database=self.connection_config["database"],
            query={
                "schema": self.connection_config.get("schema", "public"),
                "warehouse": self.connection_config.get("warehouse"),
                "role": self.connection_config.get("role")
            }
        )