```markdown
# V1 API Proxy

A minimalist Docker-based proxy for services that expose an API at a `/api/v1/...` path. This setup uses Nginx as a reverse proxy.

## Prerequisites

*   Docker
*   Docker Compose

## Setup & Configuration

1.  **Clone the repository (or download the files).**

2.  **Configure API Key:**
    Create a `.env` file in the project root with your API key for the target service:
    ```env
    API_KEY=your_actual_api_key_here
    ```

3.  **Start the services:**
    ```bash
    docker-compose up -d
    ```

## Usage

Once running, the proxy makes the target API available at:

`http://localhost/api/v1/...`

Replace `...` with the specific endpoint of the target API you wish to access (e.g., `chat/completions`). All requests to this path will be forwarded, with the `API_KEY` from your `.env` file automatically included as a bearer token.
```