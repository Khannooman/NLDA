from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.engine import URL, Engine
import logging

logger = logging.getLogger(__name__)

class DatabaseConnectionError(Exception):
    """Custom exception for database failures."""
    pass

class DatabaseWrapper(ABC):
    """Abstract base class for database wrappers."""

    def __init__(self, connection_config: Dict[str, str]):
        self.connection_config = connection_config
        self.engine: Optional[Engine] = None
        # self.metadata: MetaData

    @abstractmethod
    def default_schema(self) -> str:
        """Returns the defualt schema for database."""
        pass

    @abstractmethod
    def _create_connection_url(self) -> Engine:
        """Create a SQLAlchemy URL for the specific database connection."""
        pass