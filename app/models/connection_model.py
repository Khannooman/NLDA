from pydantic import BaseModel, Field
from typing import Union, Optional
from app.models.mssql_model import mssqlConnectionParams
from app.models.mysql_model import MySQLConnectionParams
from app.models.postgresql_model import PostgresConnectionParams

class DatabaseConnectionConfig(BaseModel):
    connection_params: Union[
        mssqlConnectionParams,
        MySQLConnectionParams,
        PostgresConnectionParams
    ] = Field(..., discriminator="db_type")
    session_id: Optional[str] = None

class Disconnect(BaseModel):
    session_id: str