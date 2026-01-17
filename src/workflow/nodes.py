from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv
from langchain.agents.structured_output import ToolStrategy

load_dotenv()

from .state import AgentState
from .prompts import ASK_QUESTIONS_PROMPT, STRUCTURED_QUESTION_RESPONSE_FORMAT, FINALIZE_DESCRIPTION_PROMPT
import logging

logger = logging.getLogger(__name__)

# ----- Initialize LLM -----
llm = ChatOpenAI(
    api_key=getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="x-ai/grok-4.1-fast",
)

# ----- Ask questions node -----

async def generate_questions_node(state: AgentState) -> dict:
    """
    Generates 1–3 new questions or decides we're ready.
    Uses create_react_agent so you can later plug in real tools (RAG/legal lookup).
    Pure node → returns delta only.
    """
    if state.is_ready or state.is_complete:
        return {}  # already done

    # iteration count for tracking
    iteration_count = state.iteration_count
    iteration_count += 1
    if iteration_count >= 3:  # Changed from > to >= to match the routing condition
        try:
            logger.info("Max iterations reached, stopping questions generation")
            return {
                "is_ready": True,
                "iteration_count": iteration_count,
            }
        except Exception as e:
            logger.exception("Error returning result after interation completion.")
            return{
                "error": str(f'Error returning result after interation completion. {e}'),
            }

    # Build agent (you can move this outside / inject if preferred)
    prompt = ASK_QUESTIONS_PROMPT.invoke(
      {
          "initial_description": state.initial_description,
          "previous_questions": "\n- " + "\n- ".join(state.questions) if state.questions else "None yet.",
          "previous_answers":   "\n- " + "\n- ".join(state.answers)   if state.answers else "None provided.",
      })

    agent = create_agent(
          llm,
          tools=[],
          system_prompt=prompt.messages[-1].content,
          response_format=ToolStrategy(STRUCTURED_QUESTION_RESPONSE_FORMAT),
      )

    try:
        parsed = (await agent.ainvoke({"messages": [{"role": "user", "content": "Please continue the intake process now."}]}))["structured_response"]
        # print('Agent output: ', parsed, '\n\n')
        new_questions = parsed.get("questions", [])
        reasoning = parsed.get("reasoning", "")
        is_complete_now = parsed.get("is_complete", False)

        update = {
            "reasoning": reasoning,
            "questions": new_questions,   # auto-appends thanks to reducer
            "iteration_count": iteration_count,
            "is_ready": is_complete_now,      # question node can set this
            "is_complete": False,             # only final node sets true
        }

        if is_complete_now:
            logger.info(f"Questions complete after {update['iteration_count']} iterations")
        else:
            logger.info(f"Asking {len(new_questions)} more questions (iter {update['iteration_count']})")

        return update

    except Exception as e:
        logger.exception("Question generation failed")
        return {
            "error": f"Question generation failed: {str(e)}",
            "iteration_count": state.iteration_count,
        }

# ----- Finalize Description Node -----
async def generate_final_description_node(state: AgentState) -> dict:
    """
    Only called when is_ready == True.
    Produces the polished professional description.
    Can also use agent/tools later (legal context, statutes...).
    """
    if not state.is_ready:
        return {"error": "Final node called without is_ready=True"}

    prompt = FINALIZE_DESCRIPTION_PROMPT.invoke(
      {
          "initial_description": state.initial_description,
          "all_questions": "\n- " + "\n- ".join(state.questions) if state.questions else "None yet.",
          "all_answers":   "\n- " + "\n- ".join(state.answers)   if state.answers else "None provided.",
      }).messages[-1].content
    # print(f'Prompt: {prompt}')

    try:
        final_text = (await llm.ainvoke(prompt)).content
        print(f'Final Description: {final_text}')
        return {
            "final_description": final_text.content if hasattr(final_text, "content") else str(final_text),
            "is_complete": True,
            "is_ready": False,  # cleanup
        }

    except Exception as e:
        logger.exception("Final description generation failed")
        return {"error": f"Final description generation failed: {str(e)}"}

# ----- Get Answers Node -----
async def get_answers(state: AgentState):
    """
    Processes user answers and returns updated state.
    This node is interrupted, so answers are provided externally.
    """
    # This node is just a placeholder for the interrupt.
    # The actual processing happens when answers are submitted via the API.
    # The answers should already be in the state by this point.
    return {"is_complete": state.is_complete, "is_ready": state.is_ready}

# ----- Test the nodes -----
if __name__ == "__main__":
    import asyncio
    
    # AgentState automatically initializes questions and answers with empty lists
    result = asyncio.run(generate_questions_node(AgentState("Some one assaulted me and i want to raise a case!")))
    print(result)
