# FastAPI Chatbot with WebSocket and Streaming Support

A simple chatbot built with FastAPI that supports:
- WebSocket connections for real-time bidirectional chat
- HTTP streaming responses using Server-Sent Events (SSE)
- Mock streaming replies (swap with OpenAI or other LLM)

## Features

- **WebSocket endpoint:** `/ws` – send JSON with `{"message": "your text"}` and receive chunks.
- **Streaming endpoint:** `POST /chat/stream` – send JSON `{"message": "..."}` and get SSE events.
- Simulated response generation with delays (easily replaceable).
- Environment configuration via `.env`.
- Docker support.

## Quick Start

### Using Python directly

1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` (optional – default port is 8000).
5. Run the server:
   ```bash
   python main.py
   ```
6. Open `http://localhost:8000` – you should see a welcome message.

### Using Docker

```bash
docker-compose up --build
```

## Usage Examples

### WebSocket (using wscat or browser)

```bash
wscat -c ws://localhost:8000/ws
> {"message": "Hello"}
< {"type": "info", "content": "Connected to chatbot"}
< {"type": "chunk", "content": "Hello "}
< {"type": "chunk", "content": "I "}
...
< {"type": "end", "content": "[DONE]"}
```

### HTTP Streaming

```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi"}'
```

You'll receive a stream of `data:` lines.

## Testing

```bash
pytest tests/
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT`   | `8000`  | Application port |

## License

MIT
