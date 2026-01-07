from langgraph.graph import StateGraph
from app.workflow.state import AgentState
from app.workflow.nodes import ask_questions_node, finalize_description_node, check_completeness_node


def create_workflow():
    """
    Creates and compiles the LangGraph workflow for the legal intake assistant.
    """
    # Create a state graph with the agent state
    workflow = StateGraph(AgentState)
    
    # Add nodes to the graph
    workflow.add_node("ask_questions", ask_questions_node)
    workflow.add_node("finalize_description", finalize_description_node)
    
    # Set the entry point
    workflow.set_entry_point("ask_questions")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "ask_questions",
        check_completeness_node,
        {
            "finalize": "finalize_description",
            "ask_questions": "ask_questions"
        }
    )
    
    # Add edges for the finalize node (it ends the workflow)
    workflow.add_edge("finalize_description", "__end__")
    
    # Compile the graph
    return workflow.compile()