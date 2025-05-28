# V1 API Proxy

A tiny Docker stack that transparently forwards requests to your upstream REST service while adding an `Authorization: Bearer` token.

## Two ways to proxy

| Path          | Container            | Use‑case                         |
| ------------- | -------------------- | -------------------------------- |
| `/api-v1/...` | **FastAPI** (Python) | streams, SSE, custom logic       |
| `/api/v1/...` | **Nginx**            | plain JSON/files, lowest latency |

## Requirements

* Docker **20.10+**
* Docker Compose **v2** (bundled with Docker Desktop)

## Quick start

```bash
# 1. configure
cp .env.example .env  # set API_KEY and API_HOST

# 2. run
docker compose up -d
```

Ready! Both endpoints are now available on `http://localhost`.
