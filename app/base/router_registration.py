from fastapi import FastAPI
from app.routers.connection_routers import ConnectionRouter

class RouterRegistration:
    def __init__(self, app: FastAPI):
        connection_router = ConnectionRouter()





        app.include_router(connection_router.router)