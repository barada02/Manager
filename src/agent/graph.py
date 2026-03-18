from langgraph.graph import END, START, StateGraph

from src.agent.nodes import llm_reasoning, route_after_llm, tool_execution
from src.agent.state import AgentState


def build_agent_app():
	graph_builder = StateGraph(AgentState)
	graph_builder.add_node("llm_reasoning", llm_reasoning)
	graph_builder.add_node("tool_execution", tool_execution)

	graph_builder.add_edge(START, "llm_reasoning")
	graph_builder.add_conditional_edges(
		"llm_reasoning",
		route_after_llm,
		{
			"tool_execution": "tool_execution",
			"end": END,
		},
	)
	graph_builder.add_edge("tool_execution", "llm_reasoning")
	return graph_builder.compile()
