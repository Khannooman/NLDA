import logging
from fastapi import APIRouter
from app.constants.route_paths import RoutePaths
from app.constants.route_tags import RouteTags
from app.models.response_model import ResponseModel
from app.models.connection_model import DatabaseConnectionConfig
from app.database_wrapper.database_wrapper_map import data_base_wrapper_map
from app.utils.agent_response import extract_response
from app.agents.sql_agent import create_sql_agent
from threading import Lock
from app.utils.utility_manager import UtilityManager
from datetime import datetime as dt

class ConnectionRouter(UtilityManager):
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if not cls._instance:
            logging.info("-----: Creating new instance of: UserRouter: -----")
            with cls._lock:
                if not cls._instance:  #Double checking the locking
                    cls._instance = super(ConnectionRouter, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "router"): # prevent re-initialization
            super().__init__()
            self.router = APIRouter(prefix=RoutePaths.API_PREFIX)
            self.setup_routers()

    def setup_routers(self):
        @self.router.post(RoutePaths.CONNECTION, tags=[RouteTags.CONNECTION], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def create_connections(connection_config: DatabaseConnectionConfig):
            question = connection_config.question
            connection_dict  =  {
                "database": connection_config.connection_params.database,
                "host": connection_config.connection_params.host,
                "password": connection_config.connection_params.password,
                "port": connection_config.connection_params.port,
                "sslmode": connection_config.connection_params.sslmode,
                "username": connection_config.connection_params.username
            }
            connection_url = data_base_wrapper_map(connection_config.connection_params.db_type)(connection_config=connection_dict).create_connection_url()
            print(connection_url)
            agent = create_sql_agent(connection_url)
            if question:
                response = extract_response(agent, question)

            return ResponseModel( 
                message=f"Successfully connected with {connection_config.connection_params.db_type} database {connection_config.connection_params.database}",
                data=response['data'],
                chart_data=response['chart_data'],
                answer=response['nl_response'],
                status_code=200
            )
                