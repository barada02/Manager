from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List


ACTORS: List[str] = ["Tom Hanks", "Scarlett Johansson", "Denzel Washington"]
CITIES: List[str] = ["Tokyo", "New York", "Paris","Berhampur"]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


async def list_actors() -> Dict[str, Any]:
    return {"actors": ACTORS, "count": len(ACTORS)}


async def list_cities() -> Dict[str, Any]:
    return {"cities": CITIES, "count": len(CITIES)}


async def _list_actors_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    return await list_actors()


async def _list_cities_handler(arguments: Dict[str, Any]) -> Dict[str, Any]:
    return await list_cities()


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


def get_gradient_tools_schema() -> List[Dict[str, Any]]:
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
    tool = TOOL_MAP.get(tool_name)
    if tool is None:
        return {"error": f"Unknown tool: {tool_name}"}
    return await tool.handler(arguments)
