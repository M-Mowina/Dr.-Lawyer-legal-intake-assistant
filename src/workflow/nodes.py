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
def generate_questions_node(state: AgentState) -> dict:
    """
    Generates 1–3 new questions or decides we're ready.
    Uses create_react_agent so you can later plug in real tools (RAG/legal lookup).
    Pure node → returns delta only.
    """
    if state.get("is_ready", False) or state.get("is_complete", False):
        return {}  # already done

    # iteration count for tracking
    iteration_count = state.get("iteration_count")
    iteration_count += 1
    if iteration_count >= 3:
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
          "initial_description": state['initial_description'],
          "previous_questions": "\n- " + "\n- ".join(state["answers_so_far"]["questions"]) if state["answers_so_far"]["questions"] else "None yet.",
          "previous_answers":   "\n- " + "\n- ".join(state["answers_so_far"]["answers"])   if state["answers_so_far"]["answers"] else "None provided.",
      })

    agent = create_agent(
          llm,
          tools=[],
          system_prompt=prompt.messages[-1].content,
          response_format=ToolStrategy(STRUCTURED_QUESTION_RESPONSE_FORMAT),
      )

    try:
        parsed = agent.invoke({"messages": [{"role": "user", "content": "Please continue the intake process now."}]})["structured_response"]

        new_questions = parsed.get("questions", [])
        reasoning = parsed.get("reasoning", "")
        is_complete_now = parsed.get("is_complete", False)

        update = {
            "answers_so_far": {
                "questions": new_questions,   # auto-appends thanks to reducer
            },
            "iteration_count": state["iteration_count"] + 1,
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
            "iteration_count": state["iteration_count"] + 1,
        }

# ----- Finalize Description Node -----
def generate_final_description_node(state: AgentState) -> dict:
    """
    Only called when is_ready == True.
    Produces the polished professional description.
    Can also use agent/tools later (legal context, statutes...).
    """
    if not state.get("is_ready"):
        return {"error": "Final node called without is_ready=True"}

    prompt = FINALIZE_DESCRIPTION_PROMPT.invoke(
      {
          "initial_description": state['initial_description'],
          "all_questions": "\n- " + "\n- ".join(state["answers_so_far"]["questions"]) if state["answers_so_far"]["questions"] else "None yet.",
          "all_answers":   "\n- " + "\n- ".join(state["answers_so_far"]["answers"])   if state["answers_so_far"]["answers"] else "None provided.",
      }).messages[-1].content

    try:
        final_text = llm.invoke(prompt).content
        print(f'Final Description: {final_text}')
        return {
            "final_description": final_text.content if hasattr(final_text, "content") else str(final_text),
            "is_complete": True,
            "is_ready": False,  # cleanup
        }

    except Exception as e:
        return {"error": f"Final description generation failed: {str(e)}"}

# ----- Dummy Get Answers Node -----
def get_answers(state: AgentState): # This is used just for better workflow visualization
  pass

# ----- Test the nodes -----
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(ask_questions_node("Some one assaulted me and i want to raise a case!", "No previous answers yet."))
    print(result)
