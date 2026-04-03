# Lab 8 — Report: The Agent is the Interface

## Task 2A — Deployed agent

Checkpoint: PASS

Nanobot gateway startup logs:
```
Starting nanobot gateway version 0.1.4.post6 on port 18790...
Channels enabled: webchat
MCP server 'lms': connected, 9 tools registered
MCP server 'webchat': connected, 1 tools registered
Agent loop started
```

Docker services running:
- nanobot: Up on port 18790
- caddy: Up on 0.0.0.0:42002->80/tcp
- qwen-code-api: Up and healthy on 127.0.0.1:42005->8080/tcp
- backend: Up on 127.0.0.1:42001->8000/tcp
- postgres: Up and healthy on 127.0.0.1:42004->5432/tcp

Files modified: nanobot/Dockerfile, nanobot/entrypoint.py, nanobot/config.json, nanobot/pyproject.toml, docker-compose.yml, caddy/Caddyfile

Status: PASS

## Task 2B — Web client

Checkpoint: PASS

Flutter web client at http://10.93.25.49:42002/flutter — serves HTML and main.dart.js
WebSocket endpoint ws://localhost:42002/ws/chat?access_key=megakey1 — accepts connections, returns agent responses

Agent conversation in Flutter:
![Flutter chat](report-images/photo_2026-04-02_22-54-37.jpg)

Architecture: browser -> caddy -> nanobot webchat -> nanobot gateway -> mcp_lms -> backend

Status: PASS

## Task 3A — Structured logging

Checkpoint: PASS

Happy-path log (request_started to request_completed with status 200):
```
2026-04-03 18:20:07,414 INFO [app.main] [trace_id=325aebb5058eb122c37641c4174a659c span_id=629f82f0753cd40f service.name=Learning Management Service] - request_started
2026-04-03 18:20:07,415 INFO [app.auth] [trace_id=325aebb5058eb122c37641c4174a659c] - auth_success
2026-04-03 18:20:07,416 INFO [app.db.items] [trace_id=325aebb5058eb122c37641c4174a659c] - db_query
2026-04-03 18:20:07,419 INFO [app.main] [trace_id=325aebb5058eb122c37641c4174a659c] - request_completed
GET /items/ HTTP/1.1 200 OK
```

Error-path log (db_query with error after stopping PostgreSQL):
```
2026-04-03 18:39:42,984 INFO [app.main] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - request_started
2026-04-03 18:39:42,985 INFO [app.auth] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - auth_success
2026-04-03 18:39:42,985 INFO [app.db.items] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - db_query
2026-04-03 18:39:43,001 ERROR [app.db.items] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - db_query
2026-04-03 18:39:43.003 | ERROR | app.routers.items:get_items:21 - items_list_failed_database_error
2026-04-03 18:39:43,004 ERROR [app.main] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - request_completed
GET /items/ HTTP/1.1 500 Internal Server Error
```

VictoriaLogs query result:
Query: `_time:10m service.name:"Learning Management Service" severity:ERROR`
Results: 3 error log entries with fields: event=db_query, severity=ERROR, trace_id=918c67aac06d55b6cf2a0030bc55011a

VictoriaLogs returns structured JSON with fields: _time, event, service.name, severity, trace_id, span_id, status, duration_ms, otelTraceID, otelSpanID

![VictoriaLogs query](report-images/victorialogs_query.png)

Status: PASS

## Task 3B — Traces

Checkpoint: PASS

Healthy trace (trace_id=325aebb5058eb122c37641c4174a659c):
- GET /items/ (2.4ms) status=200
  - auth_success (0.5ms) status=OK
  - db_query SELECT item (0.8ms) status=OK
  - request_completed (0.1ms) status=200

Error trace (trace_id=918c67aac06d55b6cf2a0030bc55011a):
- GET /items/ (22.8ms) status=500 ERROR
  - auth_success (0.1ms) status=OK
  - db_query SELECT item (13.4ms) status=ERROR connection refused
  - request_completed (0.0ms) status=500

The db_query span shows error=true with duration 13.4ms (vs 0.8ms healthy).

![VictoriaTraces healthy](report-images/victoriatraces_healthy.png)
![VictoriaTraces error](report-images/victoriatraces_error.png)

Status: PASS

## Task 3C — Observability MCP tools

Checkpoint: PASS

MCP tools registered:
- mcp_obs_logs_search — search VictoriaLogs with LogsQL
- mcp_obs_logs_error_count — count errors per service
- mcp_obs_traces_list — list recent traces
- mcp_obs_traces_get — fetch trace by ID

Nanobot startup logs:
```
MCP: registered tool 'mcp_obs_logs_search' from server 'obs'
MCP: registered tool 'mcp_obs_logs_error_count' from server 'obs'
MCP: registered tool 'mcp_obs_traces_list' from server 'obs'
MCP: registered tool 'mcp_obs_traces_get' from server 'obs'
MCP server 'obs': connected, 4 tools registered
```

Agent response — normal:
User: "Any LMS backend errors in the last 10 minutes?"
Agent: logs_error_count → 0 errors. "No errors found. Everything looks good!"

Agent response — failure (PostgreSQL stopped):
User: "Any LMS backend errors in the last 10 minutes?"
Agent: logs_error_count → 1 error. logs_search → db_query error. traces_get → error=true. "Found 1 error — db_query failed with connection refused."

Files created: mcp/mcp_obs/pyproject.toml, mcp/mcp_obs/src/mcp_obs/server.py, mcp/mcp_obs/src/mcp_obs/observability.py, nanobot/workspace/skills/observability/SKILL.md
Files modified: nanobot/pyproject.toml, nanobot/entrypoint.py, nanobot/Dockerfile, docker-compose.yml, pyproject.toml (root)

Status: PASS

## Task 4A — Multi-step investigation

Checkpoint: PASS

User: "What went wrong?"
Agent tool calls:
1. mcp_obs_logs_error_count → 1 error
2. mcp_obs_logs_search → db_query error, trace_id=918c67aa
3. mcp_obs_traces_get → error span

Agent response:
- Log evidence: ERROR in LMS, db_query failed — PostgreSQL unavailable
- Trace evidence: trace 918c67aa... db_query span 13.4ms with error=true
- Root cause: backend returned 404 but real issue is PostgreSQL connection failure

Status: PASS

## Task 4B — Proactive health check

Checkpoint: PASS

User: "Create a health check every 2 minutes..."
Agent: "Created recurring health check."

User: "List scheduled jobs."
Agent: "LMS Health Check (ID: e3429d47) — every 2 minutes"

Proactive report (PostgreSQL stopped):
- Errors: Yes — database connection failures
- Service: Learning Management Service
- Root cause: PostgreSQL unavailable

![Cron health report](report-images/task4b_cron_health_report.png)

Status: PASS

## Task 4C — Bug fix and recovery

Checkpoint: PASS

Root cause: backend/app/routers/items.py had broad `except Exception` returning 404 instead of surfacing real DB error.

Fix:
- Catch SQLAlchemyError → HTTP 500 with error message
- Catch generic Exception → HTTP 500 with logger.exception
- Log real error using loguru

Post-fix:
- Backend rebuilt and redeployed
- PostgreSQL healthy
- Agent retrieves items without misleading 404

Healthy follow-up: "System looks healthy" — no recent errors
![Healthy follow-up](report-images/task4c_healthy_followup.png)

Git commit: Fix items.py: catch SQLAlchemyError separately, return 500 instead of 404

Status: PASS
