FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy from workspace (root project) context
COPY --from=workspace pyproject.toml ./pyproject.toml
COPY --from=workspace mcp/ ./mcp/
COPY --from=workspace nanobot-websocket-channel/nanobot-channel-protocol/ ./nanobot-websocket-channel/nanobot-channel-protocol/
COPY --from=workspace nanobot-websocket-channel/mcp-webchat/ ./nanobot-websocket-channel/mcp-webchat/
COPY --from=workspace nanobot-websocket-channel/nanobot-webchat/ ./nanobot-websocket-channel/nanobot-webchat/

# Install MCP packages
RUN uv pip install --system -e ./mcp/
RUN uv pip install --system -e ./nanobot-websocket-channel/nanobot-channel-protocol/
RUN uv pip install --system -e ./nanobot-websocket-channel/mcp-webchat/
RUN uv pip install --system -e ./nanobot-websocket-channel/nanobot-webchat/

# Install main dependencies
RUN uv pip install --system nanobot-ai pydantic-settings websockets

# Copy nanobot app (from local context)
COPY . ./nanobot/

CMD ["python", "/app/nanobot/entrypoint.py"]


