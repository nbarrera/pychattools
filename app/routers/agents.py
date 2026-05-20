from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database import get_db
from app.services.agents import create_agent, get_agent_or_404
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentResponse

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=AgentResponse)
async def create(payload: AgentCreate, db: AsyncSession = Depends(get_db)):
    return await create_agent(payload, db)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get(agent_id: str, agent: Agent = Depends(get_agent_or_404)):
    return agent
