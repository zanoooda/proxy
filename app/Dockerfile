FROM python:3.11-slim
WORKDIR /app
COPY ./app/src /app
RUN pip install fastapi uvicorn httpx python-dotenv
COPY .env /app/.env
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]