import asyncio
import json
from openai import AsyncOpenAI, APIError

from app.config import settings
from app.services.tools import TOOL_SCHEMAS, dispatch

client = AsyncOpenAI(
    base_url=settings.ollama_base_url,
    api_key=settings.llm_api_key,
)

MAX_ITERATIONS = 30


class LLMError(Exception):
    pass


async def chat(messages: list[dict], db=None) -> str:
    """Agentic loop: call LLM, execute tool calls, feed results back, repeat."""
    history = list(messages)

    for _ in range(MAX_ITERATIONS):
        try:
            response = await client.chat.completions.create(
                model=settings.ollama_model,
                messages=history,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                parallel_tool_calls=False,
            )
        except APIError as e:
            raise LLMError(f"LLM error: {e.message}") from e

        msg = response.choices[0].message

        # debug — remove once tool calling is confirmed working
        print(f"[llm] tool_calls={msg.tool_calls}")
        print(f"[llm] content={msg.content!r}")

        if not msg.tool_calls:
            if msg.content:
                return msg.content
            continue

        # append assistant message with tool calls
        history.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ],
        })

        # execute each tool and append results
        await asyncio.sleep(1)
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments or "{}")
            result = await dispatch(tc.function.name, args, db)
            history.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    raise LLMError("Agent exceeded maximum iterations without producing a final answer")
