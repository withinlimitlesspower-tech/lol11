import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "FastAPI Chatbot - use /ws or /stream"}


@pytest.mark.asyncio
async def test_websocket_chat():
    # Use httpx for async websocket testing
    import httpx
    async with httpx.AsyncClient() as client_async:
        async with client_async.ws("ws://test/ws") as ws:
            # Wait for initial message
            data = await ws.receive_text()
            assert '"type": "info"' in data
            assert '"content": "Connected to chatbot"' in data

            # Send a message
            await ws.send_text('{"message": "Hello"}')

            # Collect all chunks until [DONE]
            full_response = ""
            while True:
                data = await ws.receive_text()
                if '"type": "end"' in data:
                    break
                assert '"type": "chunk"' in data
                # Extract content (simple string check)
                full_response += data
            assert len(full_response) > 0


@pytest.mark.asyncio
async def test_streaming_endpoint():
    from fastapi.testclient import TestClient
    # Use sync client for SSE (StreamingResponse yields async, but TestClient handles it)
    response = client.post("/chat/stream", json={"message": "Hi"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"

    # Read all lines
    lines = response.iter_lines()
    contents = []
    for line in lines:
        if line.startswith("data: "):
            content = line[6:]  # remove "data: "
            if '"[DONE]"' in content:
                break
            contents.append(content)
    assert len(contents) > 0
    # Note: this test might need adjustment because iter_lines() is not async.
    # For simplicity, we rely on the fact that StreamingResponse can be consumed synchronously in test.


@pytest.mark.asyncio
async def test_websocket_invalid_message():
    import httpx
    async with httpx.AsyncClient() as client_async:
        async with client_async.ws("ws://test/ws") as ws:
            # Wait for initial message
            await ws.receive_text()

            # Send invalid JSON
            await ws.send_text("not json")
            data = await ws.receive_text()
            assert '"type": "error"' in data
