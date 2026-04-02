FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./pyproject.toml
RUN uv venv && uv sync --no-dev
COPY . ./nanobot/
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "/app/nanobot/entrypoint.py"]
