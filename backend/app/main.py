import os
from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from starlette.background import BackgroundTask
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import httpx

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise RuntimeError("Environment variable OPENROUTER_API_KEY is missing")

class ChatRequest(BaseModel):
    """Schema of the request body expected by OpenRouter."""
    messages: list
    model: str = Field(default="openai/gpt-4o")
    temperature: float = 0.7
    max_tokens: int = 1200
    stream: bool = True  # enable streaming responses

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create a single shared HTTP client for the app."""
    async with httpx.AsyncClient(timeout=None) as client:
        app.state.http = client
        yield

app = FastAPI(lifespan=lifespan)

@app.post("/api/chat", response_class=StreamingResponse)
async def proxy(chat: ChatRequest):
    """Proxy request to OpenRouter and stream the SSE response back."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    # open stream but do not await context-manager directly
    stream_ctx = app.state.http.stream(
        "POST",
        OPENROUTER_API_URL,
        json=chat.dict(exclude_none=True),
        headers=headers,
    )
    resp = await stream_ctx.__aenter__()
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        await resp.aclose()
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

    # schedule context exit after streaming
    background = BackgroundTask(stream_ctx.__aexit__, None, None, None)

    # use text iterator for SSE events
    return StreamingResponse(
        resp.aiter_text(),
        status_code=resp.status_code,
        media_type="text/event-stream",
        background=background,
    )