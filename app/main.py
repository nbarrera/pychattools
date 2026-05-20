from fastapi import FastAPI

from app.routers import agents, chat

app = FastAPI(title="Chatbot API")

app.include_router(agents.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}