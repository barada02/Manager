import json
from typing import Any, Dict

from gradient import AsyncGradient

from src.agent.state import AgentState
from src.tools.traveler_tools import execute_tool, get_gradient_tools_schema
from src.utils.helper import get_required_env_var

MAX_ITERATIONS = 6
MODEL_NAME = "openai-gpt-oss-120b"


def _build_tool_call(tool_name: str, arguments: Dict[str, Any], call_id: str | None) -> Dict[str, Any]:
	return {
		"id": call_id or f"call_{tool_name}",
		"type": "function",
		"function": {
			"name": tool_name,
			"arguments": json.dumps(arguments),
		},
	}


def _normalize_tool_calls(raw_tool_calls: Any) -> list[Dict[str, Any]]:
	normalized: list[Dict[str, Any]] = []
	for raw_call in raw_tool_calls or []:
		if isinstance(raw_call, dict):
			call_id = raw_call.get("id")
			function_data = raw_call.get("function", {})
			tool_name = function_data.get("name") or raw_call.get("name")
			raw_arguments = function_data.get("arguments", raw_call.get("arguments", {}))
		else:
			call_id = getattr(raw_call, "id", None)
			function_data = getattr(raw_call, "function", None)
			tool_name = getattr(function_data, "name", None) if function_data else getattr(raw_call, "name", None)
			raw_arguments = getattr(function_data, "arguments", "{}") if function_data else getattr(raw_call, "arguments", {})

		if isinstance(raw_arguments, str):
			try:
				arguments = json.loads(raw_arguments)
			except json.JSONDecodeError:
				arguments = {}
		elif isinstance(raw_arguments, dict):
			arguments = raw_arguments
		else:
			arguments = {}

		if tool_name:
			normalized.append(_build_tool_call(tool_name, arguments, call_id))
	return normalized


async def llm_reasoning(state: AgentState) -> AgentState:
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
	tool_calls = _normalize_tool_calls(getattr(response_message, "tool_calls", []))

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
	last_assistant = state["messages"][-1]
	tool_calls = last_assistant.get("tool_calls", [])
	tool_messages = []

	for tool_call in tool_calls:
		function_data = tool_call.get("function", {})
		tool_name = function_data.get("name")
		raw_arguments = function_data.get("arguments", "{}")
		if isinstance(raw_arguments, str):
			try:
				arguments = json.loads(raw_arguments)
			except json.JSONDecodeError:
				arguments = {}
		else:
			arguments = raw_arguments or {}

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
	last_message = state["messages"][-1]
	if last_message.get("tool_calls"):
		return "tool_execution"
	return "end"


def route_after_llm(state: AgentState) -> str:
	return should_continue(state)
