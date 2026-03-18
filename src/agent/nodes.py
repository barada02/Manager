"""LangGraph node implementations.

This module contains only graph-node responsibilities:
- LLM reasoning node
- Tool execution node
- Routing condition node
"""

import json

from gradient import AsyncGradient

from src.agent.state import AgentState
from src.agent.tool_call_utils import normalize_tool_calls, parse_tool_call
from src.tools.tools import execute_tool, get_gradient_tools_schema
from src.utils.helper import get_required_env_var

MAX_ITERATIONS = 6
MODEL_NAME = "openai-gpt-oss-120b"


async def llm_reasoning(state: AgentState) -> AgentState:
	"""Call the model and append either assistant text or assistant tool calls."""
	messages = state["messages"]
	iteration_count = state["iteration_count"] + 1

	if iteration_count > MAX_ITERATIONS:
		return {
			"messages": [
				{
					"role": "assistant",
					"content": "I reached the loop limit while processing tool calls.",
				}
			],
			"final_answer": "I reached the loop limit while processing tool calls.",
			"iteration_count": iteration_count,
		}

	model_access_key = get_required_env_var("GRADIENT_MODEL_ACCESS_KEY")
	inference_client = AsyncGradient(model_access_key=model_access_key)

	try:
		response = await inference_client.chat.completions.create(
			messages=messages,
			model=MODEL_NAME,
			tools=get_gradient_tools_schema(),
		)
	except Exception as exc:
		raise RuntimeError(
			f"LLM call failed. model={MODEL_NAME}"
		) from exc

	response_message = response.choices[0].message
	content = getattr(response_message, "content", None)
	tool_calls = normalize_tool_calls(getattr(response_message, "tool_calls", []))

	if tool_calls:
		return {
			"messages": [
				{
					"role": "assistant",
					"content": content or "",
					"tool_calls": tool_calls,
				}
			],
			"final_answer": None,
			"iteration_count": iteration_count,
		}

	fallback = content or "I could not produce a final response."
	return {
		"messages": [{"role": "assistant", "content": fallback}],
		"final_answer": fallback,
		"iteration_count": iteration_count,
	}


async def tool_execution(state: AgentState) -> AgentState:
	"""Execute tool calls from the last assistant message and append tool messages."""
	last_assistant = state["messages"][-1]
	tool_calls = last_assistant.get("tool_calls", [])
	tool_messages = []

	for tool_call in tool_calls:
		tool_name, arguments = parse_tool_call(tool_call)

		result = await execute_tool(tool_name, arguments)
		tool_messages.append(
			{
				"role": "tool",
				"tool_call_id": tool_call["id"],
				"name": tool_name,
				"content": json.dumps(result),
			}
		)

	return {"messages": tool_messages, "iteration_count": state["iteration_count"]}


def should_continue(state: AgentState) -> str:
	"""Route to tool execution when tool calls are present, otherwise finish."""
	last_message = state["messages"][-1]
	if last_message.get("tool_calls"):
		return "tool_execution"
	return "end"


def route_after_llm(state: AgentState) -> str:
	return should_continue(state)
