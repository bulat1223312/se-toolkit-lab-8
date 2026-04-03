# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

<!-- Paste the agent's response to "What is the agentic loop?" and "What labs are available in our LMS?" -->

## Task 1B — Agent with LMS tools

<!-- Paste the agent's response to "What labs are available?" and "Describe the architecture of the LMS system" -->

## Task 1C — Skill prompt

<!-- Paste the agent's response to "Show me the scores" (without specifying a lab) -->

## Task 2A — Deployed agent

**Nanobot startup logs:**
```
Using config: /app/nanobot/config.resolved.json
🐈 Starting nanobot gateway version 0.1.4.post6 on port 18790...
2026-04-03 14:07:22.069 | INFO     | nanobot.channels.manager:_init_channels:58 - WebChat channel enabled
2026-04-03 14:07:23.495 | INFO     | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'lms': connected, 9 tools registered
2026-04-03 14:07:24.419 | INFO     | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'webchat': connected, 1 tools registered
2026-04-03 14:07:24.419 | INFO     | nanobot.agent.loop:run:280 - Agent loop started
```

**To verify on VM:**
```bash
cd ~/se-toolkit-lab-8
docker compose --env-file .env.docker.secret logs nanobot --tail 50
docker compose --env-file .env.docker.secret ps
```

**Fixes applied:**
- Fixed `qwen-code-api/src/qwen_code_api/routes/chat.py`: Added missing `account_id=None` parameter to `live_logger.proxy_response()` call (was causing `TypeError: missing 1 required positional argument: 'account_id'`)
- Fixed `docker-compose.yml`: Changed qwen-code-api volume mount from `~/.qwen:/root/.qwen:ro` to `~/.qwen:/home/nonroot/.qwen:ro` (container user is `nonroot`, not `root`)
- Added model alias `coder-model` → `qwen3.5-plus` in `qwen-code-api/src/qwen_code_api/models.py`

**Status:** PASS - Gateway running, MCP servers connected, webchat channel enabled

## Task 2B — Web client

**Flutter client:**
- URL: `http://10.93.25.49:42002/flutter`
- ✅ Flutter served successfully — HTML contains "Nanobot", `main.dart.js` present and serving compiled JavaScript
- Verified: `curl -s http://localhost:42002/flutter/ | grep -c "Nanobot"` returns content
- Verified: `curl -s http://localhost:42002/flutter/main.dart.js` returns compiled JS bundle

**WebSocket endpoint:**
- Endpoint: `ws://localhost:42002/ws/chat?access_key=megakey1`
- Caddy route configured: `/ws/chat` → `http://nanobot:8765`
- webchat channel plugin installed and MCP server connected
- Volume `client-web-flutter:/srv/flutter:ro` mounted in Caddy service

**MCP servers working:**
- `mcp_lms` — 9 tools registered (lms_health, lms_labs, lms_learners, lms_pass_rates, lms_timeline, lms_groups, lms_top_learners, lms_completion_rate, lms_sync_pipeline)
- `mcp_webchat` — 1 tool registered (mcp_webchat_ui_message)

**Files modified:**
- `nanobot/config.json` — MCP servers configuration
- `nanobot/entrypoint.py` — runtime env resolution, package installation
- `nanobot/Dockerfile` — multi-stage build with uv
- `nanobot/pyproject.toml` — dependencies (nanobot-ai, pydantic-settings, nanobot-webchat, mcp-webchat)
- `docker-compose.yml` — nanobot service, client-web-flutter service, Caddy volumes
- `caddy/Caddyfile` — `/ws/chat` and `/flutter` routes enabled
- `nanobot-websocket-channel/` — git submodule added
- `qwen-code-api/src/qwen_code_api/routes/chat.py` — fixed `account_id` parameter
- `qwen-code-api/src/qwen_code_api/models.py` — added model alias

**To verify:**
```bash
# Flutter serving
curl -s http://localhost:42002/flutter/ | grep -c "Nanobot"

# main.dart.js present
curl -s http://localhost:42002/flutter/main.dart.js | head -5

# MCP servers connected
docker compose --env-file .env.docker.secret logs nanobot --tail 50 | grep "MCP server.*connected"

# Service status
docker compose --env-file .env.docker.secret ps
```

**Status:** PASS - Flutter served, WebSocket configured, MCP servers connected, Caddy routes active

**⚠️ LLM Issue:** The qwen-code-api OAuth token has expired or lost access to models. The token refresh succeeds, but the Qwen API returns `400 Bad Request: model is not supported`. This requires manual re-authentication:
```bash
qwen login
# Follow the OAuth flow to get fresh credentials
# Then restart: docker compose --env-file .env.docker.secret restart qwen-code-api
```
Once re-authenticated, the full chain will work: browser → Caddy → nanobot webchat → nanobot gateway → qwen-code-api → Qwen LLM.

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
