import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import httpx

API_KEY = os.getenv("API_KEY")
API_HOST = os.getenv("API_HOST")

app = FastAPI()


@app.api_route(
    "/api-v1/{full_path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    response_class=StreamingResponse,
)
async def proxy(full_path: str, request: Request):
    """
    Simple HTTP proxy to forward requests to the target API with streaming.
    """
    target_url = f"https://{API_HOST}/api/v1/{full_path}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    content_type = request.headers.get("content-type")
    if content_type:
        headers["Content-Type"] = content_type

    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.query_params,
            content=await request.body(),
            timeout=None,
        ) as resp:
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=exc.response.status_code, detail=exc.response.text
                )

            # Stream response back to the client
            return StreamingResponse(
                resp.aiter_raw(),
                status_code=resp.status_code,
                headers={
                    k: v
                    for k, v in resp.headers.items()
                    if k.lower() not in ("transfer-encoding", "connection")
                },
            )
