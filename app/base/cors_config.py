from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

class InitCORS:
    def __init__(self, app: FastAPI):
        origins = []
        if not origins:
            origins = ["*"]
        else:
            origins = origins
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        )