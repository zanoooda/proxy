import os
from fastapi import FastAPI, Request, Response
import httpx

app = FastAPI()
API_KEY = os.getenv("API_KEY")
API_HOST = os.getenv("API_HOST")

@app.api_route(
    "/api-v1/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
)
async def proxy(path: str, request: Request):
    url = f"https://{API_HOST}/api/v1/{path}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    if content_type := request.headers.get("content-type"):
        headers["Content-Type"] = content_type
    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.request(
            request.method,
            url,
            headers=headers,
            params=request.query_params,
            content=await request.body(),
        )
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        # headers={
        #     k: v for k, v in resp.headers.items()
        #     if k.lower() not in ("transfer-encoding", "connection")
        # },
        headers=resp.headers,
        media_type=resp.headers.get("content-type"),
    )
