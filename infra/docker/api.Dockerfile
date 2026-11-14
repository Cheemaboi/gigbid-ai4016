FROM node:24-alpine AS web-builder
WORKDIR /web
COPY apps/web/package*.json ./
RUN npm ci
COPY apps/web .
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY apps apps
COPY agent agent
COPY rag rag
COPY mcp_servers mcp_servers
COPY data data
COPY --from=web-builder /web/dist /app/apps/web/dist
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["sh", "-c", "python -m uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

