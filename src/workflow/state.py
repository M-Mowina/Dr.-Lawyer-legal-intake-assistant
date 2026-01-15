from typing_extensions import Annotated
from typing import Optional, Annotated
import operator
from dataclasses import dataclass, field
@dataclass
class AnswersSoFar:
    questions: Annotated[list[str], operator.add] = field(default_factory=list)
    answers:   Annotated[list[str], operator.add] = field(default_factory=list)

@dataclass
class AgentState:
    initial_description: str
    answers_so_far: AnswersSoFar = field(default_factory=AnswersSoFar)
    reasoning: Optional[str] = None
    iteration_count: int = 0
    is_ready: bool = False         # set by question node when there is enough data for creating final description
    final_description: Optional[str] = None
    is_complete: bool = False        # final node sets this to True
    error: Optional[str] = None         # both nodes can write here