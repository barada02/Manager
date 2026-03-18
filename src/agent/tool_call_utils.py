"""Utilities for normalizing model tool calls and parsing tool arguments.

These helpers keep transport-format details out of the main node logic.
"""

import json
from typing import Any, Dict, Tuple


def build_tool_call(tool_name: str, arguments: Dict[str, Any], call_id: str | None) -> Dict[str, Any]:
    return {
        "id": call_id or f"call_{tool_name}",
        "type": "function",
        "function": {
            "name": tool_name,
            "arguments": json.dumps(arguments),
        },
    }


def normalize_tool_calls(raw_tool_calls: Any) -> list[Dict[str, Any]]:
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
            normalized.append(build_tool_call(tool_name, arguments, call_id))
    return normalized


def parse_tool_call(tool_call: Dict[str, Any]) -> Tuple[str | None, Dict[str, Any]]:
    function_data = tool_call.get("function", {})
    tool_name = function_data.get("name")
    raw_arguments = function_data.get("arguments", "{}")

    if isinstance(raw_arguments, str):
        try:
            arguments = json.loads(raw_arguments)
        except json.JSONDecodeError:
            arguments = {}
    elif isinstance(raw_arguments, dict):
        arguments = raw_arguments
    else:
        arguments = {}

    return tool_name, arguments
