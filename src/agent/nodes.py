from gradient import AsyncGradient

from src.agent.state import AgentState
from src.utils.helper import get_required_env_var


async def llm_call(state: AgentState) -> AgentState:
	model_access_key = get_required_env_var("GRADIENT_MODEL_ACCESS_KEY")
	inference_client = AsyncGradient(model_access_key=model_access_key)

	try:
		output = await inference_client.chat.completions.create(
			messages=[
				{
					"role": "user",
					"content": state["input"],
				}
			],
			model="openai-gpt-oss-120b",
		)
	except Exception as exc:
		raise RuntimeError(
			"LLM call failed. model=openai-gpt-oss-120b"
		) from exc

	return {"input": state["input"], "output": output.choices[0].message.content}
