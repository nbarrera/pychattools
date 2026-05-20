from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.agent import Agent
from app.schemas.agent import AgentCreate
from app.services.cache import cache
from app.services.database import get_db


async def create_agent(payload: AgentCreate, db: AsyncSession) -> Agent:
    agent = Agent(name=payload.name, persona=payload.persona)
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


async def get_agent(agent_id: str, db: AsyncSession) -> Agent | None:
    async def fetch_from_db():
        result = await db.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()
        if agent is None:
            return None
        return {"id": agent.id, "name": agent.name, "persona": agent.persona}

    data = await cache.find(f"persona:{agent_id}", fetcher=fetch_from_db)
    if data is None:
        return None
    return Agent(id=data["id"], name=data["name"], persona=data["persona"])


async def get_agent_or_404(agent_id: str, db: AsyncSession = Depends(get_db)) -> Agent:
    agent = await get_agent(agent_id, db)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
