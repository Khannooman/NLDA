from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage 
from typing import Dict
def extract_response(agent: StateGraph, question: str) -> Dict:
    response = agent.invoke({"messages": [HumanMessage(content=question)]})
    return {
        "data": response.get("execution_result"),
        "chart_data": response.get("final_answer")['chart_data'],
        "nl_response": response.get("final_answer")['nl_response']
    }