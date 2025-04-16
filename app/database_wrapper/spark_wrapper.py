from typing import Dict
from sqlalchemy.engine import URL
import logging

logger = logging.getLogger(__name__)

class ApacheSparkWrapper:
    """Wrapper for Apache Spark SQL."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for Apache Spark SQL."""
        return URL.create(
            drivername="hive",
            username=self.connection_config.get("username"),
            password=self.connection_config.get("password"),
            host=self.connection_config["host"],
            port=self.connection_config.get("port", 10000),
            database=self.connection_config["database"]
        )