from typing import Dict, Optional
from app.database_wrapper.database_handler import DatabaseHandler
import logging
from datetime import datetime as dt

logger = logging.getLogger(__name__)

class SessionManager:
    _instance = None
    _session: Dict[str, DatabaseHandler] = {}
    _expire_times: Dict[str, float] = {}
    _default_ttl: int = 3600 # 1 hours in second

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def store_connection(self, session_id: str, db_handler: DatabaseHandler) -> None:
        """Store a database handler for a session"""
        self._session[session_id] = db_handler
        self._expire_times[session_id] = self._default_ttl + dt.now().timestamp()
        logger.info(f"Stored connection for session {session_id} with expiry in {self._default_ttl} seconds")

    def get_connection(self, session_id: str) -> Optional[DatabaseHandler]:
        """Retrieve a database handler for a session"""
        if session_id not in self._session:
            return None
        
        if dt.now().timestamp() > self._expire_times.get(session_id, 0):
            logger.info(f"session {session_id} has expire")
            self.remove_connection(session_id=session_id)
            return None
        return self._session.get(session_id)

    def remove_connection(self, session_id: str) -> None:
        """Remove database handler from database"""
        if session_id in self._session:
            db_handler = self._session[session_id]
            db_handler.disconnect()
            del self._session[session_id]
            del self._expire_times[session_id]
            logger.info(f"Removed connection for session {session_id}")