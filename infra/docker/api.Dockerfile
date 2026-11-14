FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY apps apps
COPY agent agent
COPY rag rag
COPY mcp_servers mcp_servers
COPY data data
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["sh", "-c", "python -m uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

