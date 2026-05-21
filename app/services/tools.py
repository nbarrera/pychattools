from datetime import datetime, timezone


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Returns the current UTC date and time.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluates a single arithmetic expression and returns the numeric result. Call this tool once per expression — do not batch multiple expressions into one call.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A single arithmetic expression using only numbers and operators +-*/() — e.g. '(22 + 9) % 24'. No variables, no function calls, only literal numbers.",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_agents",
            "description": "Lists all agents registered in the system with their names, personas, and creation timestamps (ISO 8601 UTC).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def get_time() -> str:
    now = datetime.now(timezone.utc)
    return (
        f"Current UTC time: {now.strftime('%Y-%m-%d %H:%M:%S UTC')} "
        f"(hour={now.hour}, minute={now.minute}, second={now.second})"
    )


def calculate(expression: str) -> str:
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return "Error: expression contains invalid characters"
    try:
        result = eval(expression, {"__builtins__": {}})  # noqa: S307
        return str(result)
    except Exception as e:
        return f"Error: {e}"


async def list_agents(db) -> str:
    from sqlalchemy import select
    from app.models.agent import Agent

    result = await db.execute(select(Agent))
    agents = result.scalars().all()
    if not agents:
        return "No agents registered."
    return "\n".join(f"- {a.name} (created_at: {a.created_at.isoformat()}, persona: {a.persona})" for a in agents)


async def dispatch(name: str, args: dict, db) -> str:
    if name == "get_time":
        return get_time()
    if name == "calculate":
        return calculate(args.get("expression", ""))
    if name == "list_agents":
        return await list_agents(db)
    return f"Unknown tool: {name}"
