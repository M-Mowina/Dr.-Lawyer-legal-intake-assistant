from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
from typing import Optional, TypedDict
import operator

class AnswersSoFar(TypedDict):
    questions: Annotated[list[str], operator.add]
    answers:   Annotated[list[str], operator.add]


class AgentState(TypedDict):
    initial_description: str
    answers_so_far: AnswersSoFar
    iteration_count: int
    is_ready: bool               # set by question node when is_complete=True
    final_description: Optional[str]
    is_complete: bool            # final node sets this to True
    error: Optional[str]         # both nodes can write here