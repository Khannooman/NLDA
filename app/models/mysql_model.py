from pydantic import BaseModel, Field
from typing import Optional, Literal

class MySQLConnectionParams(BaseModel):
    """
    Pydantic model for MySQL connection parameters.
    """
    db_type: Literal["mysql"] = "mysql"
    host: str = Field(..., description="Host address of the MySQL server")
    port: int = Field(..., description="Port number of the MySQL server")
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
                    "port": 3306,
                    "database": "mydatabase",
                    "username": "dbuser",
                    "password": "secretpassword",
                    "sslmode": "prefer"
                }
            ]
        }
