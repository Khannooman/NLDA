from pydantic import BaseModel, Field

class Query(BaseModel):
    question: str
    session_id: str