#!/usr/bin/env python3
"""Interactive CLI client for the chatbot API."""

import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"


def post(path: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def get(path: str) -> dict:
    with urllib.request.urlopen(f"{BASE_URL}{path}") as r:
        return json.loads(r.read())


def list_agents() -> list:
    # There's no list endpoint, so we can't enumerate — return empty
    return []


def create_agent(name: str, persona: str) -> dict:
    return post("/agents/", {"name": name, "persona": persona})


def chat(agent_id: str, message: str) -> str:
    r = post(f"/agents/{agent_id}/chat", {"message": message})
    return r["content"]


def main():
    print("Chatbot CLI — type /quit to exit, /new to create an agent\n")

    agent_id = None

    if len(sys.argv) == 2:
        agent_id = sys.argv[1]
        try:
            agent = get(f"/agents/{agent_id}")
            print(f"Connected to agent: {agent['name']} ({agent_id})")
            print(f"Persona: {agent['persona']}\n")
        except urllib.error.HTTPError as e:
            print(f"Agent {agent_id} not found: {e.code}")
            sys.exit(1)

    if not agent_id:
        print("No agent ID provided. Create a new one.")
        name = input("Agent name: ").strip() or "Assistant"
        persona = input("Persona (or enter for default): ").strip() or "You are a helpful assistant."
        agent = create_agent(name, persona)
        agent_id = agent["id"]
        print(f"\nCreated agent '{agent['name']}' with ID: {agent_id}")
        print("Tip: run `python chat_cli.py {agent_id}` next time to reuse this agent.\n")

    print("─" * 50)
    while True:
        try:
            user_input = input("you: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not user_input:
            continue
        if user_input == "/quit":
            print("Bye.")
            break
        if user_input == "/new":
            name = input("Agent name: ").strip() or "Assistant"
            persona = input("Persona: ").strip() or "You are a helpful assistant."
            agent = create_agent(name, persona)
            agent_id = agent["id"]
            print(f"Switched to new agent '{agent['name']}' ({agent_id})\n")
            continue
        if user_input == "/id":
            print(f"Current agent ID: {agent_id}\n")
            continue

        try:
            reply = chat(agent_id, user_input)
            print(f"agent: {reply}\n")
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"Error {e.code}: {body}\n")
        except urllib.error.URLError as e:
            print(f"Connection error: {e.reason} — is the server running?\n")


if __name__ == "__main__":
    main()
