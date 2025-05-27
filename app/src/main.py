import os
from fastapi import FastAPI, Request, HTTPException, Response
import httpx

API_KEY = os.getenv("API_KEY")
API_HOST = os.getenv("API_HOST")

app = FastAPI()


# Simple proxy for all /api-v1 paths
def build_headers(request: Request) -> dict:
    headers = {"Authorization": f"Bearer {API_KEY}"}
    content_type = request.headers.get("content-type")
    if content_type:
        headers["Content-Type"] = content_type
    return headers


@app.api_route(
    "/api-v1/{full_path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def proxy(full_path: str, request: Request):
    target_url = f"https://{API_HOST}/api/v1/{full_path}"
    # Read body only once
    body = await request.body()
    headers = build_headers(request)
    # Forward request
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body,
                timeout=None,
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            # Return upstream error
            raise HTTPException(
                status_code=exc.response.status_code, detail=exc.response.text
            )
    # Return response to client
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers={
            k: v
            for k, v in resp.headers.items()
            if k.lower() not in ("transfer-encoding", "connection")
        },
    )
