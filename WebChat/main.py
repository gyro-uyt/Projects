# run ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

import random
import json
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, Optional

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# A simple list of random names
NAMES = [
    "Aryan",
    "Sumit",
    "Rohan",
    "Vivek",
    "Jayjeet",
    "Somya",
    "Devesh",
    "Kumkum",
    "Jatin",
    "Tanya",
]


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, dict] = {}
        self.admin: Optional[WebSocket] = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        user_id = str(uuid.uuid4())
        name = random.choice(NAMES)
        if not self.admin:
            self.admin = websocket
        self.active_connections[websocket] = {"name": name, "id": user_id}
        return user_id, name

    def disconnect(self, websocket: WebSocket):
        if websocket == self.admin:
            self.admin = None
        del self.active_connections[websocket]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    with open("index.html") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    user_id, name = await manager.connect(websocket)
    is_admin = websocket == manager.admin

    await manager.send_personal_message(
        {"type": "welcome", "user_id": user_id}, websocket
    )

    if is_admin:
        await manager.send_personal_message(
            {"type": "system", "message": "Welcome, Admin! You have special powers."},
            websocket,
        )

    await manager.broadcast(
        {"type": "system", "message": f"{name} has joined the chat"}
    )
    try:
        while True:
            data = await websocket.receive_text()
            sender_info = manager.active_connections[websocket]
            message_data = {
                "type": "chat",
                "author": sender_info["name"],
                "message": data,
                "is_admin": is_admin,
                "sender_id": sender_info["id"],
            }
            await manager.broadcast(message_data)
    except WebSocketDisconnect:
        disconnected_user = manager.active_connections[websocket]
        manager.disconnect(websocket)
        await manager.broadcast(
            {"type": "system", "message": f"{disconnected_user['name']} left the chat"}
        )
