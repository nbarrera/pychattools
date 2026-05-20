import pytest
from unittest.mock import AsyncMock, patch

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_create_agent(client):
    response = await client.post("/agents/", json={"name": "Alex", "persona": "You are Alex."})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alex"
    assert "id" in data


async def test_get_agent_not_found(client):
    response = await client.get("/agents/nonexistent-id")
    assert response.status_code == 404


async def test_chat(client):
    # create agent first
    agent = await client.post("/agents/", json={"name": "Alex", "persona": "You are Alex."})
    agent_id = agent.json()["id"]

    with patch("app.services.llm.client.chat.completions.create", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value.choices[0].message.content = "Hello!"
        response = await client.post(f"/agents/{agent_id}/chat", json={"message": "Hi"})

    assert response.status_code == 200
    assert response.json()["content"] == "Hello!"