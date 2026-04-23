import os
import json
import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="FastAPI Chatbot", version="1.0.0")

# Mock conversation history (in-memory)
conversation_history: list[dict] = []

async def stream_response(prompt: str) -> AsyncGenerator[str, None]:
    """
    Simulate a streaming response from a chatbot.
    In production, replace with call to OpenAI or similar.
    """
    # Mock: yield words with delay
    words = ["Hello", "I", "am", "a", "chatbot", ".", "You", "said:", prompt, ".", "How", "can", "I", "help", "?"]
    for word in words:
        yield f"{word} "
        await asyncio.sleep(0.1)

@app.get("/")
async def root():
    return {"message": "FastAPI Chatbot - use /ws or /stream"}

# === HTTP Streaming Endpoint ===

class ChatRequest(BaseModel):
    message: str
    stream: bool = True

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming endpoint: returns Server-Sent Events (SSE) with the chatbot reply.
    """
    prompt = request.message
    # Store user message
    conversation_history.append({"role": "user", "content": prompt})

    async def event_generator():
        async for chunk in stream_response(prompt):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        # End of stream
        yield f"data: {json.dumps({'content': '[DONE]'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

# === WebSocket Endpoint ===

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "info", "content": "Connected to chatbot"}))

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            prompt = message.get("message", "")
            if not prompt:
                await websocket.send_text(json.dumps({"type": "error", "content": "No message provided"}))
                continue

            # Store user message
            conversation_history.append({"role": "user", "content": prompt})

            # Send streaming chunks
            async for chunk in stream_response(prompt):
                await websocket.send_text(json.dumps({"type": "chunk", "content": chunk}))

            # Signal end of response
            await websocket.send_text(json.dumps({"type": "end", "content": "[DONE]"}))

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "content": str(e)}))
        raise

# === For local testing ===
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
