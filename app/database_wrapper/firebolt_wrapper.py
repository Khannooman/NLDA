from typing import Dict
from sqlalchemy.engine import URL
import logging

logger = logging.getLogger(__name__)

class FireboltWrapper:
    """Wrapper for Firebolt."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for Firebolt."""
        return URL.create(
            drivername="firebolt",
            username=self.connection_config["username"],
            password=self.connection_config["password"],
            host=self.connection_config["host"],
            database=self.connection_config["database"],
            query={
                "account_name": self.connection_config.get("account_name")
            }
        )