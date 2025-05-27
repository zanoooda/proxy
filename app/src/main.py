import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx

app = FastAPI()
API_KEY = os.getenv("API_KEY")
API_HOST = os.getenv("API_HOST")  # e.g. "openrouter.ai"

@app.api_route(
    "/api-v1/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def proxy(path: str, request: Request):
    url = f"https://{API_HOST}/api/v1/{path}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    if ct := request.headers.get("content-type"):
        headers["Content-Type"] = ct

    async with httpx.AsyncClient(timeout=None) as client:
        # Use async context manager for streaming
        async with client.stream(
            method=request.method,
            url=url,
            headers=headers,
            params=request.query_params,
            content=await request.body(),
        ) as upstream:
            excluded = {"transfer-encoding", "connection", "content-encoding"}
            filtered_headers = {
                k: v
                for k, v in upstream.headers.items()
                if k.lower() not in excluded
            }
            return StreamingResponse(
                upstream.aiter_bytes(),
                status_code=upstream.status_code,
                headers=filtered_headers,
            )
