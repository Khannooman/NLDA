from pydantic import BaseModel, Field
from typing import Optional, List, Any, TypedDict, Annotated, Dict

class AgentState(BaseModel):
    """State for the sql agent"""

    messages: List[Any] = Field(default_factory=list)
    schema_info: Optional[Dict[str, Any]] = None
    generated_query: Optional[Dict[str, Any]] = None
    validation_result: Optional[Dict[str, Any]] = None
    execution_result: Optional[Dict[str, Any]] = None
    final_answer: Optional[Dict[str, Any]] = None
    error: Optional[str] = None



