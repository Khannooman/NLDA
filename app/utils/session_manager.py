from typing import Dict, Optional
from app.database_wrapper.database_handler import DatabaseHandler
import logging

class SessionManager:
    _instance = None
    _session = Dict[str, DatabaseHandler] = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def store_connection(self, session_id: str, db_handler: DatabaseHandler) -> None:
        """Store a database handler for a session"""
        self._session[session_id] = db_handler
        logging.info(f"Stored connection for session {session_id}")

    def get_connection(self, session_id: str) -> Optional[DatabaseHandler]:
        """Retrieve a database handler for a session"""
        self._session.get(session_id)

    def remove_connection(self, session_id: str) -> None:
        """Remove database handler from database"""
        if session_id in self._session:
            db_handler = self._session[session_id]
            db_handler.disconnect()
            del self._session[session_id]
            logging.info(f"Removed connection for session {session_id}")