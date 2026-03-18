from langgraph.graph import END, START, StateGraph

from src.agent.nodes import llm_call
from src.agent.state import AgentState


def build_agent_app():
	graph_builder = StateGraph(AgentState)
	graph_builder.add_node("llm_call", llm_call)
	graph_builder.add_edge(START, "llm_call")
	graph_builder.add_edge("llm_call", END)
	return graph_builder.compile()
