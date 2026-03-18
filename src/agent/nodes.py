import os

from gradient import AsyncGradient

from src.agent.state import AgentState


async def llm_call(state: AgentState) -> AgentState:
	inference_client = AsyncGradient(
		model_access_key=os.environ.get("GRADIENT_MODEL_ACCESS_KEY")
	)

	output = await inference_client.chat.completions.create(
		messages=[
			{
				"role": "user",
				"content": state["input"],
			}
		],
		model="openai-gpt-oss-120b",
	)

	return {"input": state["input"], "output": output.choices[0].message.content}
