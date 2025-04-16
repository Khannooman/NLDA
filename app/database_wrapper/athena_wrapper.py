from typing import Dict
from sqlalchemy.engine import URL
import logging

logger = logging.getLogger(__name__)

class AWSAthenaWrapper:
    """Wrapper for AWS Athena."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> URL:
        """Create SQLAlchemy URL for AWS Athena."""
        return URL.create(
            drivername="awsathena+rest",
            username=self.connection_config.get("access_key"),
            password=self.connection_config.get("secret_key"),
            host=f"athena.{self.connection_config['region']}.amazonaws.com",
            database=self.connection_config["schema"],
            query={
                "s3_staging_dir": self.connection_config["s3_staging_dir"],
                "region_name": self.connection_config["region"]
            }
        )