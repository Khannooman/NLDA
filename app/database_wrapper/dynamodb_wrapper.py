from typing import Dict
import logging

logger = logging.getLogger(__name__)

class DynamoDBWrapper:
    """Wrapper for AWS DynamoDB."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> Dict[str, str]:
        """Create configuration dictionary for AWS DynamoDB."""
        return {
            "region_name": self.connection_config["region"],
            "aws_access_key_id": self.connection_config.get("access_key"),
            "aws_secret_access_key": self.connection_config.get("secret_key"),
            "endpoint_url": self.connection_config.get("endpoint_url")  # Optional for local DynamoDB
        }