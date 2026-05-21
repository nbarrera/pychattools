# Chatbot API

A Python backend that demonstrates **agentic AI patterns** — tool calling, multi-step reasoning loops, and agent orchestration — built on FastAPI with a pluggable LLM backend.

## What this is

This is a pet project with two learning goals:

1. **Understand agentic AI** — how tool calling, reasoning loops, and multi-agent patterns work in practice, not just in theory
2. **Learn FastAPI** — explore how to build a Python async REST API from scratch (database, caching, migrations, schemas, dependency injection) for someone coming from other backend stacks

The API layer isn't strictly necessary for the AI demo — everything could live in a CLI script. It's here intentionally, as a vehicle for learning Python backend patterns alongside the AI concepts.

## Agentic patterns demonstrated

- **Agentic loop** — the LLM doesn't just answer once; it decides whether to call tools, inspects the results, and keeps iterating until it has enough information to respond
- **Tool calling** — real functions the LLM can invoke: fetching live data, querying the database, doing arithmetic
- **Multi-agent** — multiple named agents with distinct personas, each with their own conversation history

## Stack

- **FastAPI** — async HTTP API
- **SQLAlchemy + PostgreSQL** — agent and message persistence
- **Redis** — agent caching
- **LLM** — any OpenAI-compatible endpoint (tested with Groq and Ollama)
- **Alembic** — database migrations

## Getting started

**1. Start infrastructure**
```bash
docker-compose up -d
```

**2. Run migrations**
```bash
uv run alembic upgrade head
```

**3. Configure environment**
```bash
cp .env.example .env
```
Then fill in your values — at minimum set `LLM_API_KEY`.

For Groq (recommended for tool calling): get a free API key at console.groq.com.
For local Ollama: `ollama pull llama3.2` — requires a model with tool calling support.

**4. Start the server**
```bash
uv run uvicorn app.main:app --reload
```

**5. Chat via CLI**
```bash
# Create a new agent and start chatting
python chat_cli.py

# Reconnect to an existing agent by ID
python chat_cli.py <agent_id>
```

CLI commands: `/id` to print current agent ID, `/new` to create another agent, `/quit` to exit.

## Tools

The LLM has access to four tools defined in `app/services/tools.py`:

| Tool | What it does |
|------|-------------|
| `get_time` | Returns current UTC time — the LLM cannot know this without calling it |
| `get_agent_load(agent_id)` | Returns simulated load metrics (active conversations, response time, error rate) for an agent |
| `list_agents` | Queries the database and returns all registered agents with IDs and timestamps |
| `calculate(expression)` | Evaluates an arithmetic expression deterministically |

## Try the agentic loop

Ask any agent:

> *"I have 100 new users to distribute across all agents. Check each agent's current load and tell me how many users each can take. Flag any overloaded agents."*

Watch the server log — you'll see the model call `list_agents` once, then `get_agent_load` once per agent in sequence, reasoning after each result before deciding what to check next.

## Project structure

```
app/
  main.py              — FastAPI app, router registration
  config.py            — settings from .env
  models/
    agent.py           — Agent SQLAlchemy model
    message.py         — Message SQLAlchemy model
  routers/
    agents.py          — CRUD endpoints for agents
    chat.py            — POST /{agent_id}/chat, GET /{agent_id}/conversations
  services/
    llm.py             — agentic loop (call → tool? → execute → feed back → repeat)
    tools.py           — tool schemas + implementations + dispatch
    agents.py          — agent fetch with Redis caching
    cache.py           — Redis cache wrapper
    database.py        — SQLAlchemy async session
  schemas/
    agent.py           — Pydantic schemas for agents
    chat.py            — Pydantic schemas for chat
alembic/               — database migrations
chat_cli.py            — interactive CLI client
```

## API

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/agents/` | Create a new agent |
| `GET` | `/agents/{id}` | Get agent by ID |
| `POST` | `/agents/{id}/chat` | Send a message, get a reply |
| `GET` | `/agents/{id}/conversations` | Get full conversation history |

Interactive docs available at `http://localhost:8000/docs`.
