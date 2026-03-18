"""Tool registry and tool handlers for the agent.

This file intentionally contains only tool-related concerns:
1) Mock data
2) Tool function implementations
3) Tool registry (metadata + handlers)
4) Execution and schema helpers
"""

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List

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


# -----------------------------------------------------------------------------
# Adapter handlers (normalized signature for registry)
# -----------------------------------------------------------------------------
async def _list_actors_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    return await list_actors()


async def _list_cities_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    return await list_cities()


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
