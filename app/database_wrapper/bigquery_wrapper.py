from typing import Dict
from sqlalchemy.engine import URL
import logging

logger = logging.getLogger(__name__)

class BigQueryWrapper:
    """Wrapper for Google BigQuery."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for Google BigQuery."""
        return URL.create(
            drivername="bigquery",
            username=self.connection_config.get("username"),  # Optional
            password=self.connection_config.get("password"),  # Optional
            host=self.connection_config.get("host"),  # Optional
            database=self.connection_config["project_id"],
            query={
                "dataset": self.connection_config["dataset"]
            }
        )