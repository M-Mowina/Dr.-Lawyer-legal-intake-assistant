import json
from typing import Dict, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from app.config import settings
from app.workflow.prompts import ASK_QUESTIONS_PROMPT, FINALIZE_DESCRIPTION_PROMPT, STRUCTURED_QUESTION_RESPONSE_FORMAT
from app.workflow.state import AgentState


def get_llm():
    """Factory function to get the appropriate LLM based on configuration"""
    if settings.LLM_PROVIDER == "openai":
        return ChatOpenAI(
            model="gpt-4o",  # Using a capable model for legal reasoning
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY
        )
    elif settings.LLM_PROVIDER == "anthropic":
        return ChatAnthropic(
            model="claude-3-sonnet-20240620",
            temperature=0.3,
            api_key=settings.ANTHROPIC_API_KEY
        )
    elif settings.LLM_PROVIDER == "groq":
        return ChatGroq(
            model="llama3-70b-8192",
            temperature=0.3,
            api_key=settings.GROQ_API_KEY
        )
    else:
        # Default to OpenAI if no provider specified
        return ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY
        )


async def ask_questions_node(state: AgentState) -> AgentState:
    """
    Node that asks clarifying questions to the user.
    Uses structured output to ensure consistent response format.
    """
    # Prepare context for the LLM
    previous_answers_str = json.dumps(state.get("answers_so_far", {}), indent=2)
    initial_description = state.get("initial_description", "")
    
    # Format the prompt
    prompt = ASK_QUESTIONS_PROMPT.format(
        initial_description=initial_description,
        previous_answers=previous_answers_str
    )
    
    # Get the LLM
    llm = get_llm()
    
    # Add structured output format
    structured_llm = llm.with_structured_output(STRUCTURED_QUESTION_RESPONSE_FORMAT)
    
    # Generate response
    response = await structured_llm.ainvoke([HumanMessage(content=prompt)])
    
    # Extract information from response
    questions = response["questions"]
    is_complete = response["is_complete"]
    
    # Create AI message with the questions
    ai_message_content = f"I have some questions to better understand your legal situation:\n\n" + \
                         "\n".join([f"- {q}" for q in questions])
    
    # Update state
    updated_state = state.copy()
    updated_state["current_questions"] = questions
    updated_state["is_complete"] = is_complete
    updated_state["messages"] = state.get("messages", []) + [AIMessage(content=ai_message_content)]
    updated_state["iteration_count"] = state.get("iteration_count", 0) + 1
    
    return updated_state


async def finalize_description_node(state: AgentState) -> AgentState:
    """
    Node that generates the final case description based on all collected information.
    """
    # Prepare context for the LLM
    initial_description = state.get("initial_description", "")
    all_answers = state.get("answers_so_far", {})
    
    # Format the prompt
    prompt = FINALIZE_DESCRIPTION_PROMPT.format(
        initial_description=initial_description,
        all_answers=json.dumps(all_answers, indent=2)
    )
    
    # Get the LLM (using text output for the final description)
    llm = get_llm()
    
    # Generate the final description
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    final_description = response.content
    
    # Update state
    updated_state = state.copy()
    updated_state["final_description"] = final_description
    updated_state["is_complete"] = True
    updated_state["current_questions"] = []  # No more questions to ask
    updated_state["messages"] = state.get("messages", []) + [AIMessage(content=final_description)]
    
    return updated_state


async def check_completeness_node(state: AgentState) -> str:
    """
    Conditional node that determines whether to continue asking questions or finalize.
    """
    # Check if we've reached the maximum number of iterations (safety measure)
    if state.get("iteration_count", 0) >= settings.MAX_ITERATIONS:
        return "finalize"
    
    # Check if the state indicates completion
    if state.get("is_complete", False):
        return "finalize"
    
    # Otherwise, continue asking questions
    return "ask_questions"