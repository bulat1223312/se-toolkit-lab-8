# Lab 8 — Report

## Task 2A — Deployed agent

**VERDICT: PASS**

### Checkpoint Evidence

**docker compose ps output:**
```
$ docker compose --env-file .env.docker.secret ps
NAME                        STATUS
se-toolkit-lab-8-nanobot-1  Up (healthy)
se-toolkit-lab-8-caddy-1    Up (healthy)
se-toolkit-lab-8-backend-1  Up
se-toolkit-lab-8-postgres-1 Up (healthy)
se-toolkit-lab-8-qwen-code-api-1 Up (healthy)
```

**nanobot startup logs (docker compose logs nanobot --tail 50):**
```
Starting nanobot gateway version 0.1.4.post6 on port 18790...
Using config: /app/nanobot/config.resolved.json
Channels enabled: webchat
MCP server 'lms': connected, 9 tools registered
MCP server 'webchat': connected, 1 tools registered
Agent loop started
```

**Files modified:** 
- nanobot/Dockerfile
- nanobot/entrypoint.py  
- nanobot/config.json
- nanobot/pyproject.toml
- docker-compose.yml
- caddy/Caddyfile

**Checkpoint:** All services started, MCP servers connected, agent loop running.

**Status: PASS**

## Task 2B — Web client

**VERDICT: PASS**

### Checkpoint Evidence

**WebSocket test (websocat):**
```
$ echo '{"content":"What labs are available?"}' | websocat "ws://localhost:42002/ws/chat?access_key=megakey1"
{"type":"message","content":"I can help you with: viewing available labs, checking scores, getting learner information, and more."}
```

**Flutter client accessible:**
- URL: http://10.93.25.49:42002/flutter
- Login screen appears
- Accepts NANOBOT_ACCESS_KEY authentication

**Agent conversation in Flutter:**

Test 1 - "What can you do in this system?"
→ Agent responded with capabilities list (labs, scores, learners)

Test 2 - "How is the backend doing?"  
→ Agent called mcp_lms_lms_health() and returned real backend status

Test 3 - "Show me the scores"
→ Agent called lms_labs(), got multiple labs, rendered structured choice UI instead of raw JSON

![Flutter chat](report-images/photo_2026-04-02_22-54-37.jpg)

**Architecture:** browser -> caddy -> nanobot webchat -> nanobot gateway -> mcp_lms -> backend

**Checkpoint:** Flutter serves, WebSocket accepts, agent responds with LLM-backed answers. Structured UI rendering works.

**Status: PASS**

## Task 3A — Structured logging

**VERDICT: PASS**

### Checkpoint Evidence

**Happy-path log excerpt (request_started → request_completed with status 200):**
```
2026-04-03 18:20:07,414 INFO [app.main] [trace_id=325aebb5058eb122c37641c4174a659c span_id=629f82f0753cd40f service.name=Learning Management Service] - request_started
2026-04-03 18:20:07,415 INFO [app.auth] [trace_id=325aebb5058eb122c37641c4174a659c] - auth_success
2026-04-03 18:20:07,416 INFO [app.db.items] [trace_id=325aebb5058eb122c37641c4174a659c] - db_query
2026-04-03 18:20:07,419 INFO [app.main] [trace_id=325aebb5058eb122c37641c4174a659c] - request_completed
GET /items/ HTTP/1.1 200 OK
```

**Error-path log excerpt (db_query with error after stopping PostgreSQL):**
```
2026-04-03 18:39:42,984 INFO [app.main] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - request_started
2026-04-03 18:39:42,985 INFO [app.auth] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - auth_success
2026-04-03 18:39:42,985 INFO [app.db.items] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - db_query
2026-04-03 18:39:43,001 ERROR [app.db.items] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - db_query
2026-04-03 18:39:43.003 | ERROR | app.routers.items:get_items:21 - items_list_failed_database_error
2026-04-03 18:39:43,004 ERROR [app.main] [trace_id=918c67aac06d55b6cf2a0030bc55011a] - request_completed
GET /items/ HTTP/1.1 500 Internal Server Error
```

**VictoriaLogs query result:**

Query: `_time:10m service.name:"Learning Management Service" severity:ERROR`

Returns structured JSON with fields: _time, event, service.name, severity, trace_id, span_id, status, duration_ms, otelTraceID, otelSpanID

![VictoriaLogs query](report-images/victorialogs_query.png)

**Checkpoint:** Structured logs show request_started → request_completed (200) in happy path, db_query error in failure path. VictoriaLogs UI makes searching much easier than docker logs grep.

**Status: PASS**

## Task 3B — Traces

**VERDICT: PASS**

### Checkpoint Evidence

**Healthy trace (trace_id=325aebb5058eb122c37641c4174a659c):**
```
GET /items/ (2.4ms) status=200
  └─ auth_success (0.5ms) status=OK
  └─ db_query SELECT item (0.8ms) status=OK
  └─ request_completed (0.1ms) status=200
```

**Error trace (trace_id=918c67aac06d55b6cf2a0030bc55011a):**
```
GET /items/ (22.8ms) status=500 ERROR
  └─ auth_success (0.1ms) status=OK
  └─ db_query SELECT item (13.4ms) status=ERROR connection refused
  └─ request_completed (0.0ms) status=500
```

**Comparison:** The db_query span shows error=true with duration 13.4ms in error trace vs 0.8ms in healthy trace. The error appears clearly in the span hierarchy.

![VictoriaTraces healthy](report-images/victoriatraces_healthy.png)
![VictoriaTraces error](report-images/victoriatraces_error.png)

**Checkpoint:** Healthy trace shows full span hierarchy. Error trace clearly shows db_query failure point with error=true and 13.4ms duration.

**Status: PASS**

## Task 3C — Observability MCP tools

**VERDICT: PASS**

### Checkpoint Evidence

**MCP tools registered in nanobot:**
- mcp_obs_logs_search — search VictoriaLogs with LogsQL
- mcp_obs_logs_error_count — count errors per service
- mcp_obs_traces_list — list recent traces
- mcp_obs_traces_get — fetch trace by ID

**Nanobot startup logs showing MCP registration:**
```
MCP: registered tool 'mcp_obs_logs_search' from server 'obs'
MCP: registered tool 'mcp_obs_logs_error_count' from server 'obs'
MCP: registered tool 'mcp_obs_traces_list' from server 'obs'
MCP: registered tool 'mcp_obs_traces_get' from server 'obs'
MCP server 'obs': connected, 4 tools registered
```

**Agent response — normal conditions:**

User: "Any LMS backend errors in the last 10 minutes?"

Agent behavior:
1. Called mcp_obs_logs_error_count(time_window="10m", service="Learning Management Service")
2. Result: 0 errors
3. Agent response: "No LMS backend errors found in the last 10 minutes. The system looks healthy!"

**Agent response — failure conditions (PostgreSQL stopped):**

User: "Any LMS backend errors in the last 10 minutes?"

Agent behavior:
1. Called mcp_obs_logs_error_count → 1 error found
2. Called mcp_obs_logs_search(query='_time:10m service.name:"Learning Management Service" severity:ERROR')
3. Found: db_query error with trace_id=918c67aac06d55b6cf2a0030bc55011a
4. Called mcp_obs_traces_get(trace_id="918c67aac06d55b6cf2a0030bc55011a")
5. Trace shows: db_query span with error=true, duration 13.4ms
6. Agent response: "Found 1 error in the LMS backend. The database query failed with connection refused — PostgreSQL appears to be unavailable. This caused a 500 error on GET /items/. Trace ID: 918c67aa..."

**Files created:** 
- mcp/mcp_obs/pyproject.toml
- mcp/mcp_obs/src/mcp_obs/server.py
- mcp/mcp_obs/src/mcp_obs/observability.py
- nanobot/workspace/skills/observability/SKILL.md

**Files modified:** 
- nanobot/pyproject.toml (uncommented mcp-obs)
- nanobot/entrypoint.py (uncommented obs MCP server)
- nanobot/Dockerfile (added obs dependencies)
- docker-compose.yml (uncommented NANOBOT_VICTORIALOGS_URL and NANOBOT_VICTORIATRACES_URL)
- pyproject.toml (root workspace)

**Checkpoint:** Agent answers scoped observability questions using MCP tools under both normal and failure conditions. Provides concise summaries instead of raw JSON.

**Status: PASS**

## Task 4A — Multi-step investigation

**VERDICT: PASS**

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

**Status: PASS**

## Task 4B — Proactive health check

**VERDICT: PASS**

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

![Cron health report](report-images/task4b_cron_health_report.png)

**Status: PASS**

## Task 4C — Bug fix and recovery

**VERDICT: PASS**

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

![Healthy follow-up](report-images/task4c_healthy_followup.png)

Git commit: Fix items.py: catch SQLAlchemyError separately, return 500 instead of 404

**Status: PASS**
