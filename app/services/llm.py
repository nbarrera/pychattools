from openai import AsyncOpenAI,APIError

from app.config import settings

client = AsyncOpenAI(
    base_url=settings.ollama_base_url,
    api_key="ollama", # required but not used
)


class LLMError(Exception):
    pass

async def chat(messages: list[dict]) -> str:
    try:
        response = await client.chat.completions.create(
            model=settings.ollama_model,
            messages=messages,
        )
        return response.choices[0].message.content
    except APIError as e:
        raise LLMError(f"LLM error: {e.message}") from e
