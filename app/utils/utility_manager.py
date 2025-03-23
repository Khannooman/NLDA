import hashlib
import logging
from typing import Dict, List
from app.utils.env_manager import EnvManager
from app.utils.api_error_handler import CatchAPIException

class UtilityManager(EnvManager, CatchAPIException):
    def __init__(self) -> None:
        super().__init__()