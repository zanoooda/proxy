import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from starlette.background import BackgroundTask
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import httpx

API_KEY = os.getenv("API_KEY")
API_HOST = os.getenv("API_HOST")


def get_lifespan():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with httpx.AsyncClient(timeout=None) as client:
            app.state.http = client
            yield

    return lifespan


app = FastAPI(lifespan=get_lifespan())


class ChatRequest(BaseModel):
    model: str = Field(...)
    messages: list
    temperature: float = Field(None)
    top_p: float = Field(None)
    stream: bool = Field(False)


@app.api_route(
    "/api-v1/{full_path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    response_class=StreamingResponse,
)
async def proxy(full_path: str, request: Request):
    target_url = f"https://{API_HOST}/api/v1/{full_path}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    if request.headers.get("content-type"):
        headers["Content-Type"] = request.headers.get("content-type")
    stream_ctx = app.state.http.stream(
        method=request.method,
        url=target_url,
        headers=headers,
        params=request.query_params,
        content=await request.body(),
        timeout=None,
    )
    resp = await stream_ctx.__aenter__()
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        await resp.aclose()
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.text
        )
    background = BackgroundTask(stream_ctx.__aexit__, None, None, None)
    return StreamingResponse(
        resp.aiter_raw(),
        status_code=resp.status_code,
        headers={
            k: v
            for k, v in resp.headers.items()
            if k.lower() not in ("transfer-encoding", "connection")
        },
        background=background,
    )
