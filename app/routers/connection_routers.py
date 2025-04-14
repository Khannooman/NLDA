import logging
from fastapi import APIRouter, HTTPException
from app.constants.route_paths import RoutePaths
from app.constants.route_tags import RouteTags
from app.models.response_model import ResponseModel
from app.models.connection_model import DatabaseConnectionConfig, Disconnect
from app.models.query_model import Query
from app.database_wrapper.database_wrapper_map import data_base_wrapper_map
from app.utils.agent_response import extract_response
from app.agents.sql_agent import create_sql_agent
from threading import Lock
from app.utils.utility_manager import UtilityManager
from app.utils.session_manager import SessionManager
from app.database_wrapper.schema_parser import SchemaParser
from app.database_wrapper.database_handler import DatabaseHandler
from app.embeddings.chroma import VectorSearch
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
            self.session_manager = SessionManager()
            self.vector_search = VectorSearch()
            self.setup_routers()

    def setup_routers(self):
        @self.router.post(RoutePaths.CONNECTION, tags=[RouteTags.QUERY], response_model=ResponseModel)
        @self.catch_api_exceptions
        async def create_connections(connection_config: DatabaseConnectionConfig):
            # generate session_id if not provided
            session_id = connection_config.session_id or self.generate_uuid()

            # check if already connected
            if self.session_manager.get_connection(session_id=session_id):
                raise HTTPException(status_code=400, detail="Session already connected")
            
            connection_dict  =  {
                "database": connection_config.connection_params.database,
                "host": connection_config.connection_params.host,
                "password": connection_config.connection_params.password,
                "port": connection_config.connection_params.port,
                "sslmode": connection_config.connection_params.sslmode,
                "username": connection_config.connection_params.username
            }

            connection_url = data_base_wrapper_map(connection_config.connection_params.db_type)(connection_config=connection_dict).create_connection_url()
            
            #Intialize DatabaseHandler and connect
            db_handler = DatabaseHandler(connection_url=connection_url)
            if not db_handler.connect():
                raise HTTPException(status_code=500, detail="Failed to connect")
            
            # Store the connection
            self.session_manager.store_connection(session_id, db_handler)

            # parse scheam to get the tables documents for making embedding
            schema_parser = SchemaParser(db_handler=db_handler)
            table_doc = schema_parser.generate_schema_documents()
            try:
                self.vector_search.create_vector_embeddings(
                    docs=table_doc,
                    session_id=session_id,
                    )
            except Exception as e:
                logging.error(f"Failed to store embeddings: {e}")
                pass

            return ResponseModel( 
                message=f"Successfully connected with {connection_config.connection_params.db_type} database {connection_config.connection_params.database}",
                status_code=200,
                session_id=session_id
            )
        
        @self.router.post(RoutePaths.QUERY, tags=RouteTags.QUERY, response_model=ResponseModel)
        @self.catch_api_exceptions
        async def query(query_request: Query):
            ## fetch the session
            session_id = query_request.session_id
            question = query_request.question

            db_handler = self.session_manager.get_connection(session_id)
            if not db_handler:
                raise HTTPException(status_code=400, detail="No active connection for this session. Please connect first")
            
            agent = create_sql_agent(db_handler, session_id=session_id)
            response = extract_response(agent, question)

            return ResponseModel(
                message="Query executed successfully",
                data=response.get("data"),
                chart_data=response.get("chart_data"),
                answer=response.get("nl_response"),
                status_code=200,
                session_id=session_id
            )
        
        @self.router.post(RoutePaths.DISCONNECT, tags=RouteTags.QUERY, response_model=ResponseModel)
        @self.catch_api_exceptions
        async def disconnect_database(disconnec_request: Disconnect):
            session_id = disconnec_request.session_id

            db_handler = self.session_manager.get_connection(session_id=session_id)
            if not db_handler:
                raise HTTPException(status_code=400, detail="No active connection for this session")
            
            self.session_manager.remove_connection(session_id=session_id)
            return ResponseModel(
                message="Database connection closed successfully"
            )



