# Lab 8 — Report: The Agent is the Interface

## Task 2A — Deployed agent

**Status: PASS**

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

Checkpoint: All services started, MCP servers connected, agent loop running.

## Task 2B — Web client

**Status: PASS**

Flutter web client at http://10.93.25.49:42002/flutter — serves HTML and main.dart.js
WebSocket endpoint ws://localhost:42002/ws/chat?access_key=megakey1 — accepts connections, returns agent responses

Agent conversation in Flutter:
![Flutter chat](report-images/photo_2026-04-02_22-54-37.jpg)

Architecture: browser -> caddy -> nanobot webchat -> nanobot gateway -> mcp_lms -> backend

Checkpoint: Flutter serves, WebSocket accepts, agent responds with LLM-backed answers.

## Task 3A — Structured logging

**Status: PASS**

### Happy-path log excerpt (request_started to request_completed with status 200):
```
2026-04-03 18:20:07,414 INFO [app.main] [trace_id=325aebb5058eb122c37641c4174a659c span_id=629f82f0753cd40f service.name=Learning Management Service] - request_started
2026-04-03 18:20:07,415 INFO [app.auth] [trace_id=325aebb5058eb122c37641c4174a659c] - auth_success
2026-04-03 18:20:07,416 INFO [app.db.items] [trace_id=325aebb5058eb122c37641c4174a659c] - db_query
2026-04-03 18:20:07,419 INFO [app.main] [trace_id=325aebb5058eb122c37641c4174a659c] - request_completed
GET /items/ HTTP/1.1 200 OK
```

### Error-path log excerpt (db_query with error after stopping PostgreSQL):
```
2026-04-03 18:39:42,984 INFO [app.main] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - request_started
2026-04-03 18:39:42,985 INFO [app.auth] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - auth_success
2026-04-03 18:39:42,985 INFO [app.db.items] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - db_query
2026-04-03 18:39:43,001 ERROR [app.db.items] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - db_query
2026-04-03 18:39:43.003 | ERROR | app.routers.items:get_items:21 - items_list_failed_database_error
2026-04-03 18:39:43,004 ERROR [app.main] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - request_completed
GET /items/ HTTP/1.1 500 Internal Server Error
```

### VictoriaLogs query result:
```
Query: _time:10m service.name:"Learning Management Service" severity:ERROR
Results: 3 error log entries found with fields: event=db_query, severity=ERROR, trace_id=918c67aac06d55b6cf2a0030bc55011a
```

VictoriaLogs returns structured JSON logs with fields: _time, event, service.name, severity, trace_id, span_id, status, duration_ms, otelTraceID, otelSpanID

![VictoriaLogs query result](report-images/victorialogs_query.png)

## Task 3B — Traces

**Status: PASS**

### Healthy trace span hierarchy (trace_id=325aebb5058eb122c37641c4174a659c):
```
GET /items/ (2.4ms) status=200
  auth_success (0.5ms) status=OK
  db_query SELECT item (0.8ms) status=OK
  request_completed (0.1ms) status=200
```

![VictoriaTraces healthy trace](report-images/victoriatraces_healthy.png)

### Error trace span hierarchy (trace_id=918c67aac06d55b6cf2a0030bc55011a):
```
GET /items/ (22.8ms) status=500 ERROR
  auth_success (0.1ms) status=OK
  db_query SELECT item (13.4ms) status=ERROR connection refused
  request_completed (0.0ms) status=500
```

The db_query span shows error=true with duration 13.4ms (vs normal 0.8ms in healthy trace).

![VictoriaTraces error trace](report-images/victoriatraces_error.png)

## Task 3C — Observability MCP tools

**Status: PASS**

### MCP tools registered in nanobot:
```
MCP: registered tool 'mcp_obs_logs_search' from server 'obs'
MCP: registered tool 'mcp_obs_logs_error_count' from server 'obs'
MCP: registered tool 'mcp_obs_traces_list' from server 'obs'
MCP: registered tool 'mcp_obs_traces_get' from server 'obs'
MCP server 'obs': connected, 4 tools registered
```

### Observability tool output — normal conditions:
User: "Any LMS backend errors in the last 10 minutes?"
Agent tool call: mcp_obs_logs_error_count → {"service": "Learning Management Service", "minutes": 10, "error_count": 0}
Agent response: "No LMS backend errors found in the last 10 minutes. Everything looks good!"

### Observability tool output — failure conditions (PostgreSQL stopped):
User: "Any LMS backend errors in the last 10 minutes?"
Agent tool calls:
1. mcp_obs_logs_error_count → {"service": "Learning Management Service", "minutes": 10, "error_count": 1}
2. mcp_obs_logs_search → Found db_query error with trace_id=918c67aac06d55b6cf2a0030bc55011a
3. mcp_obs_traces_get → Trace shows db_query span with error=true, duration 13.4ms
Agent response: "Found 1 error — db_query failed with connection refused. PostgreSQL was stopped."

### Files created:
- mcp/mcp_obs/pyproject.toml
- mcp/mcp_obs/src/mcp_obs/server.py (4 MCP tools)
- mcp/mcp_obs/src/mcp_obs/observability.py (helper functions)
- nanobot/workspace/skills/observability/SKILL.md

### Files modified:
- nanobot/pyproject.toml (added mcp-obs dependency)
- nanobot/entrypoint.py (added obs MCP server config)
- nanobot/Dockerfile (added mcp-obs install step)
- docker-compose.yml (added VICTORIALOGS_URL and VICTORIATRACES_URL env vars)
- pyproject.toml root (added mcp/mcp_obs to workspace)

## Task 4A — Multi-step investigation

**Status: PASS**

User: "What went wrong?"

Agent tool calls:
1. mcp_obs_logs_error_count → 1 error in last 10 minutes
2. mcp_obs_logs_search → found db_query error with trace_id=918c67aa
3. mcp_obs_traces_get → trace shows error span

Agent response:
Based on my investigation:
- Log evidence: ERROR in Learning Management Service, db_query failed — PostgreSQL unavailable
- Trace evidence: trace 918c67aa... db_query span 13.4ms with error=true (vs normal 0.8ms)
- Root cause: backend returned 404 but real issue is PostgreSQL connection failure. The error handler in items.py masks all exceptions as 404.

## Task 4B — Proactive health check

**Status: PASS**

User: "Create a health check for this chat that runs every 2 minutes..."
Agent: "Created recurring health check. Runs every 2 minutes, checks for errors, posts summary."

User: "List scheduled jobs."
Agent: "LMS Health Check (ID: e3429d47) — every 2 minutes — checks backend errors, posts report"

Proactive health report (PostgreSQL stopped):
- Time window: Last 2 minutes
- Errors found: Yes — database connection failures
- Service: Learning Management Service
- Root cause: PostgreSQL unavailable
- Recommendation: Restart PostgreSQL

![Cron health check proactive report](report-images/task4b_cron_health_report.png)

## Task 4C — Bug fix and recovery

**Status: PASS**

Root cause: backend/app/routers/items.py had broad `except Exception` that caught ALL errors and returned HTTP 404 "Items not found" instead of surfacing the real database error.

Fix applied:
- Catch `SQLAlchemyError` specifically → return HTTP 500 with actual error message
- Catch generic `Exception` separately → return HTTP 500 with logger.exception
- Log the real error using loguru for debugging

Post-fix verification:
- Backend rebuilt and redeployed
- PostgreSQL running and healthy
- Agent can retrieve items/labs without misleading 404
- Database errors now properly reported as HTTP 500

Healthy follow-up:
- Health check reports "System looks healthy" — no recent errors
- All LMS backend requests completing successfully

![Healthy follow-up after bug fix](report-images/task4c_healthy_followup.png)

Git commit: Fix items.py: catch SQLAlchemyError separately, return 500 instead of 404
