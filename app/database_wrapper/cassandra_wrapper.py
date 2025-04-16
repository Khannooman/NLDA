from typing import Dict
import logging

logger = logging.getLogger(__name__)

class ApacheCassandraWrapper:
    """Wrapper for Apache Cassandra."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> Dict[str, str]:
        """Create configuration dictionary for Apache Cassandra."""
        return {
            "contact_points": [self.connection_config["host"]],
            "port": self.connection_config.get("port", 9042),
            "keyspace": self.connection_config["keyspace"],
            "username": self.connection_config.get("username"),
            "password": self.connection_config.get("password")
        }