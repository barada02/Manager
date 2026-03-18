import operator
from typing import Annotated, Any, Dict, List, TypedDict


class AgentState(TypedDict):
	messages: Annotated[List[Dict[str, Any]], operator.add]
	final_answer: str | None
	iteration_count: int
