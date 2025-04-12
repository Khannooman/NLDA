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
    question: Optional[str] = Field(..., description="User inputs")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "connection_params": {
                        "db_type": "postgresql",
                        "host": "localhost",
                        "port": 5432,
                        "database": "mydatabase",
                        "username": "dbuser",
                        "password": "secretpassword",
                        "sslmode": "prefer"
                    }
                }
            ],
            "questions": "Total Number of Customers"
        }
