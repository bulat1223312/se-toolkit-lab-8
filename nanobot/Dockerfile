FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./pyproject.toml
RUN uv pip install --system nanobot-ai pydantic-settings
COPY . ./nanobot/
# Install MCP servers at runtime via entrypoint
CMD ["python", "/app/nanobot/entrypoint.py"]
