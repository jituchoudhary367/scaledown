from langgraph.graph import StateGraph, END
from .state import AgentState
from .core import (
    research_node,
    critic_node,
    synthesizer_node,
    writer_node
)

def should_continue(state: AgentState):
    """
    Decide whether to proceed to synthesis or retry research.
    """
    confidence = state.get("confidence", 0.0)
    iteration = state.get("iteration", 0)
    
    # Proceed to synthesis if confidence >= 0.5 OR after 5 iterations
    
    if confidence >= 0.5 or iteration > 5:
        return "synthesizer"  # Fixed: must match node name
    else:
        return "research"

def create_research_graph():
    """
    Builds and returns the compiled research graph.
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("researcher", research_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("writer", writer_node)

    # Set entry point
    workflow.set_entry_point("researcher")

    # Add edges
    workflow.add_edge("researcher", "critic")
    
    # Conditional edge from critic
    workflow.add_conditional_edges(
        "critic",
        should_continue,
        {
            "synthesizer": "synthesizer",
            "research": "researcher"
        }
    )
    
    workflow.add_edge("synthesizer", "writer")
    workflow.add_edge("writer", END)

    return workflow.compile()
