---
name: observability
description: Query logs, traces, and error counts from observability stack
always: true
---

# Observability Skill

You have access to observability MCP tools for querying VictoriaLogs and VictoriaTraces.

## Available Tools

- `logs_search` — Search VictoriaLogs with a LogsQL query. Parameters: `query` (str), `limit` (int, default 10).
- `logs_error_count` — Count ERROR-level log entries for a service. Parameters: `service` (str, default "Learning Management Service"), `minutes` (int, default 60).
- `traces_list` — List recent traces for a service. Parameters: `service` (str, default "Learning Management Service"), `limit` (int, default 5).
- `traces_get` — Get a full trace by trace ID. Parameters: `trace_id` (str).

## Strategy Rules

### When the user asks about errors
1. First call `logs_error_count` to check if there are recent errors
2. If errors exist, call `logs_search` with a scoped query like `_time:10m severity:ERROR` to find details
3. Extract any `trace_id` fields from the log entries
4. Call `traces_get` with the trace_id to see the full failure path
5. Summarize findings concisely — do NOT dump raw JSON

### When the user asks about system health
1. Call `logs_error_count` with a narrow time window (e.g., 10 minutes)
2. Report the result: "No errors in the last 10 minutes" or "Found N errors"
3. If errors found, use `logs_search` to show the most relevant ones

### When the user asks about a specific service
1. Scope the query to that service using `service.name:"<service>"` in the LogsQL query
2. Use a narrow time window to avoid unrelated historical errors

### Field names in this stack
- `service.name` — the service name (e.g., "Learning Management Service")
- `severity` — log level (INFO, WARN, ERROR, DEBUG)
- `event` — event name (e.g., "request_started", "db_query", "auth_success")
- `trace_id` — links to VictoriaTraces

### Example queries
- `_time:10m severity:ERROR` — recent errors across all services
- `_time:10m service.name:"Learning Management Service" severity:ERROR` — LMS errors only
- `_time:5m event:db_query severity:ERROR` — database errors
- `trace_id:"abc123..."` — logs for a specific trace

### Response formatting
- Always summarize in natural language
- Include timestamps and error counts
- If you find a trace ID, mention it and describe the failure path
- Never output raw JSON unless the user explicitly asks
