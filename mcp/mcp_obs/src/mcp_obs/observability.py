"""Helper functions for querying VictoriaLogs and VictoriaTraces."""

from __future__ import annotations

import httpx


def search_logs(victorialogs_url: str, query: str, limit: int = 10) -> list[dict]:
    """Search VictoriaLogs with a LogsQL query.

    POST to {url}/select/logsql/query with form-encoded query and limit.
    Response is newline-delimited JSON, one log entry per line.
    """
    endpoint = f"{victorialogs_url}/select/logsql/query"
    body = f"query={query}&limit={limit}"
    resp = httpx.post(
        endpoint,
        content=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30.0,
    )
    resp.raise_for_status()
    results: list[dict] = []
    for line in resp.text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            results.append(__import__("json").loads(line))
        except __import__("json").JSONDecodeError:
            results.append({"_raw": line})
    return results


def count_errors(
    victorialogs_url: str,
    service: str = "Learning Management Service",
    minutes: int = 60,
) -> int:
    """Count ERROR-level log entries for *service* over the last *minutes* minutes."""
    query = f'_time:{minutes}m service.name:"{service}" severity:ERROR'
    entries = search_logs(victorialogs_url, query, limit=10_000)
    return len(entries)


def list_traces(
    victoriatraces_url: str,
    service: str = "Learning Management Service",
    limit: int = 5,
) -> list[dict]:
    """List recent traces from VictoriaTraces (Jaeger-compatible API)."""
    endpoint = f"{victoriatraces_url}/select/jaeger/api/traces"
    resp = httpx.get(
        endpoint,
        params={"service": service, "limit": limit},
        timeout=30.0,
    )
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict):
        return data.get("data", [])
    if isinstance(data, list):
        return data
    return []


def get_trace(victoriatraces_url: str, trace_id: str) -> dict | None:
    """Retrieve a single trace by its ID from VictoriaTraces."""
    endpoint = f"{victoriatraces_url}/select/jaeger/api/traces/{trace_id}"
    resp = httpx.get(endpoint, timeout=30.0)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, dict):
        return data.get("data")
    return None
