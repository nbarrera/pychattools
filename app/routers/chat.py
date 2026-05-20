from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.database import get_db
from app.services.agents import get_agent_or_404
from app.services.llm import chat as llm_chat
from app.models.agent import Agent
from app.models.message import Message
from app.schemas.chat import ChatRequest, ChatResponse, ConversationHistory

router = APIRouter(prefix="/agents", tags=["chat"])


@router.post("/{agent_id}/chat", response_model=ChatResponse)
async def chat(
    agent_id: str,
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(get_agent_or_404),
):
    history = await db.execute(select(Message).where(Message.agent_id == agent_id))
    messages = history.scalars().all()

    llm_messages = [{"role": "system", "content": agent.persona}]
    llm_messages += [{"role": m.role, "content": m.content} for m in messages]
    llm_messages.append({"role": "user", "content": payload.message})

    reply = await llm_chat(llm_messages)

    user_msg = Message(agent_id=agent_id, role="user", content=payload.message)
    assistant_msg = Message(agent_id=agent_id, role="assistant", content=reply)
    db.add(user_msg)
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)

    return ChatResponse(id=assistant_msg.id, role="assistant", content=reply)


@router.get("/{agent_id}/conversations", response_model=ConversationHistory)
async def get_conversation(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    agent: Agent = Depends(get_agent_or_404),
):
    result = await db.execute(select(Message).where(Message.agent_id == agent_id))
    messages = result.scalars().all()

    return ConversationHistory(
        agent_id=agent_id,
        messages=[ChatResponse(id=m.id, role=m.role, content=m.content) for m in messages],
    )
