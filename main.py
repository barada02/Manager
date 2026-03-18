from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class AppState(TypedDict):
	message: str


def clean_input_node(state: AppState) -> AppState:
	return {"message": state["message"].strip()}


def decorate_message_node(state: AppState) -> AppState:
	return {"message": f"LangGraph says: {state['message']} 🚀"}


def build_graph():
	graph_builder = StateGraph(AppState)
	graph_builder.add_node("clean_input", clean_input_node)
	graph_builder.add_node("decorate_message", decorate_message_node)

	graph_builder.add_edge(START, "clean_input")
	graph_builder.add_edge("clean_input", "decorate_message")
	graph_builder.add_edge("decorate_message", END)

	return graph_builder.compile()


def main() -> None:
	graph = build_graph()
	initial_state: AppState = {"message": " hello from module 1 "}
	result = graph.invoke(initial_state)
	print(result)


if __name__ == "__main__":
	main()
