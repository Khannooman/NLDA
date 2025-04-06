from typing import Dict
from sqlalchemy.engine import URL
from app.database_wrapper.database_handler import DatabaseHandler
import logging

logger = logging.getLogger(__name__)

class MySQLWrapper:
    """Wrapper for MySQL."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for MySQL."""
        return URL.create(
            "MySQL+mysqlconnector",
            username=self.connection_config["username"],
            password=self.connection_config["password"],
            host=self.connection_config["host"],
            port=self.connection_config.get("port", 3306),
            database=self.connection_config["database"],
        )