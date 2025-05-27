import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
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
    if ct := request.headers.get("content-type"):
        headers["Content-Type"] = ct
    async with httpx.AsyncClient(timeout=None) as client:
        upstream = await client.stream(
            method=request.method,
            url=url,
            headers=headers,
            params=request.query_params,
            content=await request.body(),
        )

        excluded = {"transfer-encoding", "connection", "content-encoding"}
        filtered_headers = {
            k: v for k, v in upstream.headers.items() if k.lower() not in excluded
        }

        return StreamingResponse(
            upstream.aiter_bytes(),
            status_code=upstream.status_code,
            headers=filtered_headers,
        )
