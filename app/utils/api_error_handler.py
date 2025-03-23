import json
import logging
from functools import wraps
from fastapi import HTTPException
from fastapi.responses import JSONResponse

class CatchAPIException:
    def __init__(self) -> None:
        pass