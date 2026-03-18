"""Tool registry and tool handlers for the agent.

This file intentionally contains only tool-related concerns:
1) Mock data
2) Tool function implementations
3) Tool registry (metadata + handlers)
4) Execution and schema helpers
"""

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List
from urllib import error, parse, request

from src.utils.helper import get_required_env_var

# -----------------------------------------------------------------------------
# Mock data (safe local data for learning/testing)
# -----------------------------------------------------------------------------
ACTORS: List[str] = ["Tom Hanks", "Scarlett Johansson", "Denzel Washington"]
CITIES: List[str] = ["Tokyo", "New York", "Paris", "Berhampur"]


# -----------------------------------------------------------------------------
# Tool metadata contract
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


# -----------------------------------------------------------------------------
# Tool implementations (business logic)
# -----------------------------------------------------------------------------
async def list_actors() -> Dict[str, Any]:
    return {"actors": ACTORS, "count": len(ACTORS)}


async def list_cities() -> Dict[str, Any]:
    return {"cities": CITIES, "count": len(CITIES)}


async def ask_external_rag_agent(question: str) -> Dict[str, Any]:
    """Call an external DO-hosted RAG agent for math-related queries."""
    try:
        endpoint = get_required_env_var("EXTERNAL_AGENT_ENDPOINT")
        access_key = get_required_env_var("EXTERNAL_AGENT_ACCESS_KEY")
    except RuntimeError as exc:
        return {
            "error": "External RAG agent env configuration is missing/invalid.",
            "details": str(exc),
        }

    base_url = endpoint.rstrip("/")
    if base_url.endswith("/api/v1/chat/completions"):
        url = base_url
    else:
        url = parse.urljoin(f"{base_url}/", "api/v1/chat/completions")

    payload = {
        "messages": [{"role": "user", "content": question}],
        "stream": False,
        "include_functions_info": True,
        "include_retrieval_info": True,
        "include_guardrails_info": True,
    }

    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_key}",
        },
        method="POST",
    )

    def _post() -> Dict[str, Any]:
        try:
            with request.urlopen(req, timeout=30) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw)
        except error.HTTPError as exc:
            error_text = exc.read().decode("utf-8", errors="replace")
            return {
                "error": f"External agent HTTP {exc.code}",
                "details": error_text,
            }
        except error.URLError as exc:
            return {
                "error": "External agent request failed",
                "details": str(exc.reason),
            }
        except Exception as exc:
            return {
                "error": "External agent unexpected error",
                "details": str(exc),
            }

    return await asyncio.to_thread(_post)


# -----------------------------------------------------------------------------
# Adapter handlers (normalized signature for registry)
# -----------------------------------------------------------------------------
async def _list_actors_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    return await list_actors()


async def _list_cities_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    return await list_cities()


async def _ask_external_rag_agent_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    question = str(arguments.get("question", "")).strip()
    if not question:
        return {
            "error": "Missing required argument: question",
            "hint": "Pass {\"question\": \"your question\"}",
        }
    return await ask_external_rag_agent(question)


# -----------------------------------------------------------------------------
# Tool registry (single source of truth)
# -----------------------------------------------------------------------------
TOOLS: List[ToolSpec] = [
    ToolSpec(
        name="list_actors",
        description="Return a simple mock list of actor names.",
        parameters={"type": "object", "properties": {}},
        handler=_list_actors_handler,
    ),
    ToolSpec(
        name="list_cities",
        description="Return a simple mock list of city names.",
        parameters={"type": "object", "properties": {}},
        handler=_list_cities_handler,
    ),
    ToolSpec(
        name="ask_external_rag_agent",
        description="Use the hosted external RAG agent for math-related queries and return its full response JSON.",
        parameters={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Math-related user question to send to external RAG agent",
                }
            },
            "required": ["question"],
        },
        handler=_ask_external_rag_agent_handler,
    ),
]

TOOL_MAP: Dict[str, ToolSpec] = {tool.name: tool for tool in TOOLS}


# -----------------------------------------------------------------------------
# Public helpers used by the LLM node
# -----------------------------------------------------------------------------
def get_gradient_tools_schema() -> List[Dict[str, Any]]:
    """Return OpenAI/Gradient-compatible tool schema generated from TOOL registry."""
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }
        for tool in TOOLS
    ]


async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Run tool by name with safe fallback for unknown tool names."""
    tool = TOOL_MAP.get(tool_name)
    if tool is None:
        return {"error": f"Unknown tool: {tool_name}"}
    return await tool.handler(arguments)
