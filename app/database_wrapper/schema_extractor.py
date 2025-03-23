from typing import Dict, List
from app.database_wrapper.base_wrapper  import DatabaseWrapper, DatabaseConnectionError
from app.database_wrapper.mssql_wrapper import MSSQLWrapper
from app.database_wrapper.mysql_wrapper import MySQLWrapper
from app.database_wrapper.postgres_wrapper import PostgreSQLWrapper
from app.enums.database_type import DatabaseType
import logging

logger = logging.getLogger(__name__)

def extract_schema(db_type: DatabaseType, connection_config: Dict[str, str]) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    """
    Extract schema from a specified database type using the provided connection config.
    
    Args:
        db_type (str): Type of database
        connection_config (Dict[str, str]): Database connection details
    
    Returns:
        Dict: Schema structure with tables and columns
    
    Raises:
        ValueError: If db_type is unsupported
        DatabaseConnectionError: If connection fails
    """

    # Mapping of Database enum in wrapper classes
    db_wrapper_map ={
        DatabaseType.MSSQL: MSSQLWrapper,
        DatabaseType.MYSQL: MySQLWrapper,
        DatabaseType.POSTGRESSQL: PostgreSQLWrapper
    }

    # check if the database type is not supported
    if db_type not in db_wrapper_map:
        unsupported_type = db_type.value 
        logging.error(f"Unsupported database type: {unsupported_type}")
        raise ValueError(f"Unsupported database type: {unsupported_type}")
    
    wrapper_class = db_wrapper_map[db_type]
    wrapper = wrapper_class(connection_config=connection_config)
    
    try:
        wrapper.connect()
        schema = wrapper.get_schema()
        return schema
    except DatabaseConnectionError as e:
        logging.error(f"Schema extraction failed for {db_type.value}: {str(e)}")
        raise e
    finally:
        wrapper.disconnect()