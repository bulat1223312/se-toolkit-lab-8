"""Stdio MCP server for observability (VictoriaLogs + VictoriaTraces)."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

server = Server("obs")

_victorialogs_url: str = ""
_victoriatraces_url: str = ""

# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class _NoArgs(BaseModel):
    """Empty input model for tools that need no user-facing parameters."""


class _LogsSearchArgs(BaseModel):
    query: str = Field(description="LogsQL query string.")
    limit: int = Field(default=10, ge=1, description="Max log entries to return.")


class _ErrorCountArgs(BaseModel):
    service: str = Field(
        default="Learning Management Service",
        description='Service name to filter on (service.name field).',
    )
    minutes: int = Field(
        default=60, ge=1, description="Look-back window in minutes.",
    )


class _TracesListArgs(BaseModel):
    service: str = Field(
        default="Learning Management Service",
        description="Service name to filter traces.",
    )
    limit: int = Field(default=5, ge=1, description="Max traces to return.")


class _TraceGetArgs(BaseModel):
    trace_id: str = Field(description="Jaeger trace ID to retrieve.")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _text(value: Any) -> list[TextContent]:
    """Serialize arbitrary data to a JSON text block."""
    return [TextContent(type="text", text=json.dumps(value, ensure_ascii=False, default=str))]


async def _search_logs(args: _LogsSearchArgs) -> list[TextContent]:
    endpoint = f"{_victorialogs_url}/select/logsql/query"
    body = f"query={args.query}&limit={args.limit}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            endpoint,
            content=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
    results: list[dict] = []
    for line in resp.text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            results.append(json.loads(line))
        except json.JSONDecodeError:
            results.append({"_raw": line})
    return _text(results)


async def _error_count(args: _ErrorCountArgs) -> list[TextContent]:
    query = f'_time:{args.minutes}m service.name:"{args.service}" severity:ERROR'
    endpoint = f"{_victorialogs_url}/select/logsql/query"
    body = f"query={query}&limit=10000"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            endpoint,
            content=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
    count = sum(1 for line in resp.text.splitlines() if line.strip())
    return _text({"service": args.service, "minutes": args.minutes, "error_count": count})


async def _traces_list(args: _TracesListArgs) -> list[TextContent]:
    endpoint = f"{_victoriatraces_url}/select/jaeger/api/traces"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(endpoint, params={"service": args.service, "limit": args.limit})
        resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict):
        traces = data.get("data", [])
    elif isinstance(data, list):
        traces = data
    else:
        traces = []
    return _text(traces)


async def _traces_get(args: _TraceGetArgs) -> list[TextContent]:
    endpoint = f"{_victoriatraces_url}/select/jaeger/api/traces/{args.trace_id}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(endpoint)
        resp.raise_for_status()
    data = resp.json()
    trace = data.get("data") if isinstance(data, dict) else None
    return _text(trace)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_Registry = tuple[type[BaseModel], Callable[..., Awaitable[list[TextContent]]], Tool]

_TOOLS: dict[str, _Registry] = {}


def _register(
    name: str,
    description: str,
    model: type[BaseModel],
    handler: Callable[..., Awaitable[list[TextContent]]],
) -> None:
    schema = model.model_json_schema()
    schema.pop("$defs", None)
    schema.pop("title", None)
    _TOOLS[name] = (
        model,
        handler,
        Tool(name=name, description=description, inputSchema=schema),
    )


_register(
    "logs_search",
    "Search VictoriaLogs with a LogsQL query. Returns matching log entries.",
    _LogsSearchArgs,
    _search_logs,
)
_register(
    "logs_error_count",
    "Count ERROR-level log entries for a service over a time window.",
    _ErrorCountArgs,
    _error_count,
)
_register(
    "traces_list",
    "List recent traces for a service from VictoriaTraces.",
    _TracesListArgs,
    _traces_list,
)
_register(
    "traces_get",
    "Retrieve a full trace (with spans) by trace ID.",
    _TraceGetArgs,
    _traces_get,
)


# ---------------------------------------------------------------------------
# MCP handlers
# ---------------------------------------------------------------------------


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [entry[2] for entry in _TOOLS.values()]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    entry = _TOOLS.get(name)
    if entry is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    model_cls, handler, _ = entry
    try:
        args = model_cls.model_validate(arguments or {})
        return await handler(args)
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main() -> None:
    global _victorialogs_url, _victoriatraces_url
    _victorialogs_url = os.environ.get("VICTORIALOGS_URL", "http://victorialogs:9428").rstrip("/")
    _victoriatraces_url = os.environ.get("VICTORIATRACES_URL", "http://victoriatraces:10428").rstrip("/")
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
