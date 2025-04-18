from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.middleware import SecurityHeadersMiddleware

class InitCORS:
    def __init__(self, app: FastAPI):
        origins = []
        if not origins:
            origins = ["*"]
        else:
            origins = origins

        # add Scurity Middleware
        app.add_middleware(SecurityHeadersMiddleware)
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        )
