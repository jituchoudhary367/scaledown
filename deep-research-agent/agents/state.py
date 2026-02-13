from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    task: str
    research_data: Optional[Dict[str, Any]]
    critique: Optional[Dict[str, Any]]
    synthesis: Optional[Dict[str, Any]]
    report: Optional[str]
    confidence: float
    iteration: int
