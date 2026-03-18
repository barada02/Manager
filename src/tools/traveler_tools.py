from typing import Any, Dict, List


ACTORS: List[str] = ["Tom Hanks", "Scarlett Johansson", "Denzel Washington"]
CITIES: List[str] = ["Tokyo", "New York", "Paris"]


async def list_actors() -> Dict[str, Any]:
    return {"actors": ACTORS, "count": len(ACTORS)}


async def list_cities() -> Dict[str, Any]:
    return {"cities": CITIES, "count": len(CITIES)}


async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if tool_name == "list_actors":
        return await list_actors()
    if tool_name == "list_cities":
        return await list_cities()
    return {"error": f"Unknown tool: {tool_name}"}
