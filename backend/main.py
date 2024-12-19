from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, Request, Header
from typing import Annotated
from fastapi.responses import HTMLResponse
from starlette.concurrency import run_until_first_complete
from fastapi.templating import Jinja2Templates
from broadcaster import Broadcast
import os
import logging

logger = logging.getLogger('uvicorn.error')

BROADCAST_URL = os.environ.get("BROADCAST_URL", "memory://")
broadcast = Broadcast(BROADCAST_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting up")
        logger.info("Setting up broadcast")
        logger.info(f"Broadcast URL: {BROADCAST_URL}")
        await broadcast.connect()
        yield
    finally:
        await broadcast.disconnect()
        logger.info("Broadcast disconnected")
        logger.info("Shutting down")

app = FastAPI(lifespan=lifespan,root_path="/api")
templates = Jinja2Templates(directory="./templates")

async def chatroom_ws_receiver(websocket: WebSocket):
    async for message in websocket.iter_text():
        await broadcast.publish(channel="chatroom", message=message)

async def chatroom_ws_sender(websocket: WebSocket):
    async with broadcast.subscribe(channel="chatroom") as subscriber:
        async for event in subscriber:
            await websocket.send_text(event.message)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/lobby")
async def chatroom_ws(websocket: WebSocket):
    logger.info("Websocket connection established")
    await websocket.accept()
    await run_until_first_complete(
        (chatroom_ws_receiver, {"websocket": websocket}),
        (chatroom_ws_sender, {"websocket": websocket}),
    )
