from datetime import datetime
import json
import os
import logging
import traceback
from typing import Optional, Dict, Any, Union, List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError
from app.utils.utility_manager import UtilityManager
import decimal
import uuid
from fastapi import HTTPException
from app.models.response_model import StatusCodes
import datetime as dt


class PostgreSQLManager(UtilityManager):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self, 
        host: Optional[str] = None, 
        database: Optional[str] = None, 
        user: Optional[str] = None, 
        password: Optional[str] = None, 
        port: Optional[str] = None,
        schema: Optional[str] = None,
        ssl_mode: Optional[str] = None
    ):
        # Prevent re-initialization
        if hasattr(self, 'initialized') and self.initialized:
            return

        # Use environment variables as fallback
        self.host = host or os.getenv('POSTGRES_DB_HOST')
        self.database = database or os.getenv('POSTGRES_DB_NAME')
        self.user = user or os.getenv('POSTGRES_DB_USER')
        self.password = password or os.getenv('POSTGRES_DB_PASSWORD')
        self.port = port or int(os.getenv('POSTGRES_DB_PORT', '5432'))
        self.schema = schema or os.getenv('POSTGRES_DB_SCHEMA')
        self.ssl_mode = ssl_mode or os.getenv('POSTGRES_SSLMODE', 'prefer')

        try:
            # Construct connection URL
            connection_url = URL.create(
                'postgresql+psycopg2',
                username=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database,
                query={'sslmode': self.ssl_mode}
            )
            self.connection_url = connection_url
            # Log connection details (masking sensitive info)
            logging.info(f"Connecting to PostgreSQL at {self.host}:{self.port}/{self.database}")

            # Create engine
            self.engine = create_engine(connection_url, pool_pre_ping=True)
            
            # Create scoped session
            session_factory = sessionmaker(bind=self.engine)
            self._session = scoped_session(session_factory)

            # Verify connection
            with self.engine.connect() as connection:
                logging.info("Database connection established successfully")

            self.initialized = True

        except Exception as e:
            logging.error(f"Failed to initialize database connection: {e}")
            logging.debug(traceback.format_exc())
            raise

    def get_session(self):
        """Get a database session."""
        return self._session()
    
    def convert_value(self, value):
        """Convert Python types to JSON-compatible formats"""
        if value is None:
            return None
        elif isinstance(value, (dt.date, dt.datetime)):
            return value.isoformat()
        elif isinstance(value, decimal.Decimal):
            return float(value)
        elif isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, (list, dict)):
            return json.loads(json.dumps(value, default=str))
        return value
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None, 
        fetch_one: bool = False,
        return_json: bool = False
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], Any]:
        """Execute database query with proper type handling"""
        session = None
        try:
            session = self.get_session()

            # Convert parameters for database
            if params:
                processed_params = {}
                for key, value in params.items():
                    if isinstance(value, (dt.date, dt.datetime)):  # Fixed isinstance check
                        processed_params[key] = value
                    elif isinstance(value, str) and len(value) == 36:  # UUID string check
                        try:
                            uuid.UUID(value)  # Validate it's actually a UUID
                            processed_params[key] = value
                        except ValueError:
                            processed_params[key] = value
                    else:
                        processed_params[key] = value
                params = processed_params
            result = session.execute(text(query), params or {})

            if query.strip().lower().startswith(("select", "with")) or "returning" in query.lower():
                if return_json:
                    columns = result.keys()
                    if fetch_one:
                        row = result.fetchone()
                        if not row:
                            return None
                        data = {
                            col: self.convert_value(val)
                            for col, val in zip(columns, row)
                        }
                    else:
                        rows = result.fetchall()
                        data = [
                            {
                                col: self.convert_value(val)
                                for col, val in zip(columns, row)
                            }
                            for row in rows
                        ]
                else:
                    data = result.fetchone() if fetch_one else result.fetchall()
            else:
                data = result.rowcount  # Return number of affected rows for INSERT/UPDATE/DELETE

            session.commit()
            return data
        
        except Exception as e:
            if session:
                session.rollback()
            logging.error(f"Error executing query: {str(e)}")
            logging.error(traceback.format_exc())  # Add traceback for debugging
            raise HTTPException(
                status_code=StatusCodes.INTERNAL_SERVER_ERROR_500,
                detail=f"Query execution error: {str(e)}"
            )
        finally:
            if session:
                session.close()