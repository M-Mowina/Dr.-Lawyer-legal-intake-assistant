from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents.structured_output import ToolStrategy

load_dotenv()

from .prompts import ASK_QUESTIONS_PROMPT, STRUCTURED_QUESTION_RESPONSE_FORMAT


# ----- Initialize LLM -----
llm = ChatOpenAI(
    api_key=getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="x-ai/grok-4.1-fast",
)

# ----- Ask questions node -----
async def ask_questions_node(initial_description, previous_answers, system_prompt : ChatPromptTemplate = ASK_QUESTIONS_PROMPT, strategy : ToolStrategy = ToolStrategy(STRUCTURED_QUESTION_RESPONSE_FORMAT)):
    if not previous_answers:
        previous_answers = "No previous answers yet."

    # Create a chat prompt template with the custom system message
    
    prompt = system_prompt.invoke(
        {
            "initial_description": initial_description,
            "previous_answers": previous_answers,
        }
    )
    # Create the OpenAI functions agent with the custom prompt
    agent = create_agent(
        llm,
        tools=[],
        system_prompt=prompt.messages[-1].content,
        response_format=strategy,
    )

    result = await agent.ainvoke({"messages": [{"role": "user", "content": " "}]})
    return result["structured_response"]



if __name__ == "__main__":
    import asyncio
    result = asyncio.run(ask_questions_node("Some one assaulted me and i want to raise a case!", "No previous answers yet."))
    print(result)
