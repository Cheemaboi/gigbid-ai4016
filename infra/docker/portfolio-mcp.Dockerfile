FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
COPY mcp_servers mcp_servers
COPY data data
RUN pip install --no-cache-dir .
ENV MCP_TRANSPORT=streamable-http
EXPOSE 8000
CMD ["python", "-m", "mcp_servers.portfolio.server"]
