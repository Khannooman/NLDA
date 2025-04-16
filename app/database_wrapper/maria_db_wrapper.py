from typing import Dict
from sqlalchemy.engine import URL
import logging

logger = logging.getLogger(__name__)

class MariaDBWrapper:
    """Wrapper for MariaDB."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for MariaDB."""
        return URL.create(
            drivername="mysql+mysqlconnector",
            username=self.connection_config["username"],
            password=self.connection_config["password"],
            host=self.connection_config["host"],
            port=self.connection_config.get("port", 3306),
            database=self.connection_config["database"]
        )