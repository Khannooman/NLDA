from typing import Dict
import logging

logger = logging.getLogger(__name__)

class RedisWrapper:
    """Wrapper for Redis."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> Dict[str, str]:
        """Create configuration dictionary for Redis."""
        return {
            "host": self.connection_config["host"],
            "port": self.connection_config.get("port", 6379),
            "db": self.connection_config.get("db", "0"),
            "username": self.connection_config.get("username"),
            "password": self.connection_config.get("password")
        }