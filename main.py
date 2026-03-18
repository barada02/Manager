"""Entrypoint for the modular LangGraph agent."""

from typing import Dict

from gradient_adk import RequestContext, entrypoint

from src.agent import AgentState, build_agent_app


@entrypoint
async def main(input: Dict, context: RequestContext):
    initial_state: AgentState = {
        "messages": [
            {
                "role": "user",
                "content": input.get("prompt", ""),
            }
        ],
        "final_answer": None,
        "iteration_count": 0,
    }
    app = build_agent_app()
    result = await app.ainvoke(initial_state)
    return result["final_answer"]
