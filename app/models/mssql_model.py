from pydantic import BaseModel, Field
from typing import Optional, Literal

class mssqlConnectionParams(BaseModel):
    """
    Pydantic model for MSSQL connection parameters.
    """
    db_type: Literal["mssql"] = "mssql"
    host: str = Field(..., description="Host address of the MSSQL server")
    port: int = Field(..., description="Port number of the MSSQL server")
    database: str = Field(..., description="Name of the database to connect to")
    username: str = Field(..., description="Username for authentication")
    password: str = Field(..., description="Password for authentication")
    sslmode: Optional[str] = Field(
        None,
        description="SSL mode for the connection (e.g., 'require', 'prefer', 'allow'). ")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "host": "localhost",
                    "port": 1433,
                    "database": "mydatabase",
                    "username": "dbuser",
                    "password": "secretpassword",
                    "sslmode": "prefer"
                }
            ]
        }