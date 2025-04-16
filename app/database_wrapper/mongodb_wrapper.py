from typing import Dict
import logging

logger = logging.getLogger(__name__)

class MongoDBWrapper:
    """Wrapper for MongoDB."""
    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
    
    def create_connection_url(self) -> str:
        """Create connection string for MongoDB."""
        username = self.connection_config.get("username")
        password = self.connection_config.get("password")
        host = self.connection_config["host"]
        port = self.connection_config.get("port", 27017)
        database = self.connection_config["database"]
        
        if username and password:
            return f"mongodb://{username}:{password}@{host}:{port}/{database}"
        return f"mongodb://{host}:{port}/{database}"