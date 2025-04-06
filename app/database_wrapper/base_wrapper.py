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

    # def connect(self) -> None:
    #     """Establish a connection to the database"""
    #     try:
    #         connection_url = self._create_connection_url()
    #         self.engine = create_engine(connection_url)
    #         # self.metadata.reflect(bind=self.engine)
    #         logger.info(f"Connected to {self.__class__.__name__} database: {self.connection_config['database']}")
    #     except Exception as e:
    #         logger.error(f"Failed to connect to {self.__class__.__name__}: {str(e)}")
    #         raise DatabaseConnectionError(f"Connecton Failed: {str(e)}")
        
    # def disconnect(self) -> None:
    #     """Close the database connection."""
    #     if self.engine:
    #         self.engine.dispose()
    #         logger.info(f"Disconnected from {self.__class__.__name__} : {self.connection_config['database']}")

    # def get_schema(self) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    #     """
    #     Extract comprehensive schema metadata from the database, including tables, columns,
    #     primary keys, foreign keys, and constraints.

    #     Returns:
    #         Dict: Schema structure with tables, columns, keys, relationships, and constraints
    #               Format: {schema_name: {table_name: {"columns": [], "primary_keys": [], "foreign_keys": [], "constraints": []}}}
        
    #     Raises:
    #         DatabaseConnectionError: If no active connection exists
    #     """
    #     if not self.engine:
    #         raise DatabaseConnectionError("No active database connection")
        
    #     schema: Dict[str, Dict[str, List[Dict[str, str]]]] = {}
    #     schema_name = self.connection_config.get('schema', self.default_schema())

    #     with self.engine.connect() as conn:
    #         inspector = inspect(self.engine)
    #         tables = inspector.get_table_names(schema=schema_name)

    #         for table_name in tables:
    #             table_info = {
    #                 "columns": [],
    #                 "primary_keys": [],
    #                 "foreign_keys": [],
    #                 "constraints" : []
    #             }

    #             # Columns
    #             columns = inspector.get_columns(table_name, schema=schema_name)
    #             for column in columns:
    #                 table_info["columns"].append({
    #                     "column_name": column.get("name"),
    #                     "data_type": str(column.get("type")),
    #                     "nullable": column.get("nullable"),
    #                     "default": str(column.get("default")),
    #                     "comment": column.get("comment")
    #                 })

    #             # Primary Keys
    #             primary_keys = inspector.get_pk_constraint(table_name, schema=schema_name)
    #             for key in primary_keys.get("constrained_columns"):
    #                 table_info["primary_keys"].append(key)

    #             # Foreign Keys
    #             fks = inspector.get_foreign_keys(table_name, schema=schema_name)
    #             for fk in fks:
    #                 table_info["foreign_keys"].append({
    #                     "constrained_columns": fk["constrained_columns"],
    #                     "referred_schema": fk["referred_schema"] or schema_name,
    #                     "referred_table": fk["referred_table"],
    #                     "referred_columns": fk["referred_columns"],
    #                     "name": fk.get("name")
    #                 })
                 
    #             # Unique Constraints and Other Constraints
    #             unique_constraints = inspector.get_unique_constraints(table_name, schema=schema_name)
    #             for uc in unique_constraints:
    #                 table_info["constraints"].append({
    #                     "type": "unique",
    #                     "name": uc["name"],
    #                     "columns": uc["column_names"]
    #                 })

    #             # For databases supporting check constraints (e.g., PostgreSQL)
    #             if hasattr(inspector, "get_check_constraints"):
    #                 check_constraints = inspector.get_check_constraints(table_name, schema=schema_name)
    #                 for cc in check_constraints:
    #                     table_info["constraints"].append({
    #                         "type": "check",
    #                         "name": cc["name"],
    #                         "sqltext": cc["sqltext"]
    #                     })

    #             schema.setdefault(schema_name, {})[table_name] = table_info

    #     logger.info(f"Schema extracted for {schema_name} with {len(tables)} tables, include keys and constraints")
    #     return schema

