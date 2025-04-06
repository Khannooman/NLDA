from typing import Dict, List, Union
from app.database_wrapper.base_wrapper  import DatabaseWrapper, DatabaseConnectionError
from app.database_wrapper.mssql_wrapper import MSSQLWrapper
from app.database_wrapper.mysql_wrapper import MySQLWrapper
from app.database_wrapper.postgres_wrapper import PostgreSQLWrapper
from app.enums.database_type import DatabaseType
import logging

logger = logging.getLogger(__name__)

def data_base_wrapper_map(db_type: DatabaseType) ->  Union[MSSQLWrapper, MySQLWrapper, PostgreSQLWrapper]:
    """
    Args:
        db_type (str): Type of database
    Returns:
        Dict: return the wrapper class for the database type
    Raises:
        ValueError: If db_type is unsupported
    """

    # Mapping of Database enum in wrapper classes
    db_wrapper_map ={
        DatabaseType.MSSQL.value: MSSQLWrapper,
        DatabaseType.MYSQL.value: MySQLWrapper,
        DatabaseType.POSTGRESSQL.value: PostgreSQLWrapper
    }
    
    # check if the database type is not supported
    if db_type not in db_wrapper_map:
        unsupported_type = db_type
        logging.error(f"Unsupported database type: {unsupported_type}")
        raise ValueError(f"Unsupported database type: {unsupported_type}")
    
    wrapper_class = db_wrapper_map[db_type]
    return wrapper_class