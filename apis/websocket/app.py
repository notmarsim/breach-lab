"""Nexora WebSocket Telemetry Service (ws.nexora.test)."""

from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

app = FastAPI(title="Nexora WebSocket Telemetry")


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "api-websocket"})


@app.websocket("/ws/events")
async def ws_events(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({"event": "connected", "service": "nexora-telemetry"})
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_json({"echo": msg, "status": "ok"})
    except WebSocketDisconnect:
        return
