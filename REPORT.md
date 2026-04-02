# Lab 8 — Report

## Task 2A — Deployed agent

**Nanobot startup logs:**
```
Using config: /app/nanobot/config.resolved.json
🐈 Starting nanobot gateway version 0.1.4.post6 on port 18790...
2026-04-02 21:43:01.790 | INFO | nanobot.channels.manager:_init_channels:58 - WebChat channel enabled
✓ Channels enabled: webchat
✓ Heartbeat: every 1800s
2026-04-02 21:43:03.550 | INFO | nanobot.channels.manager:start_all:91 - Starting webchat channel...
2026-04-02 21:43:03.551 | INFO | nanobot.channels.manager:_dispatch_outbound:119 - Outbound dispatcher started
2026-04-02 21:43:04.449 | INFO | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'lms': connected, 9 tools registered
2026-04-02 21:43:05.334 | INFO | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'webchat': connected, 1 tools registered
2026-04-02 21:43:05.334 | INFO | nanobot.agent.loop:run:280 - Agent loop started
```

**Configuration:**
- `config.resolved.json` generated from environment variables
- `apiKey`: Set from `LLM_API_KEY` environment variable
- `apiBase`: `http://qwen-code-api:8080/v1`
- WebChat channel enabled on port 8765

**Files modified:**
- `nanobot/entrypoint.py` - Fixed to properly override config values from environment
- `nanobot/config.json` - Updated to use environment variable placeholders
- `docker-compose.yml` - Enabled nanobot service
- `caddy/Caddyfile` - Enabled `/ws/chat` route

![Nanobot logs](report-images/Снимок%20экрана%202026-04-02%20224300.png)

**Status: PASS**

## Task 2B — Web client

**Flutter client:**
- URL: `http://10.93.25.49:42002/flutter`
- Flutter served at /flutter with `main.dart.js` present
- Login protected by `NANOBOT_ACCESS_KEY=megakey1`

**WebSocket endpoint:**
- Endpoint: `ws://localhost:42002/ws/chat?access_key=megakey1`
- WebSocket handshake: `HTTP/1.1 101 Switching Protocols`
- MCP server 'webchat': connected, 1 tool registered (`mcp_webchat_ui_message`)

**Files modified:**
- `docker-compose.yml` - Enabled `client-web-flutter` service and Caddy dependencies
- `caddy/Caddyfile` - Enabled `/flutter*` route with volume mount
- `pyproject.toml` - Added nanobot-websocket-channel workspace members
- `nanobot/pyproject.toml` - Added nanobot-webchat and mcp-webchat dependencies
- `nanobot/entrypoint.py` - Added webchat channel and MCP server configuration

**Architecture:**
```
browser -> caddy (port 42002) -> nanobot webchat channel (port 8765) -> nanobot gateway -> mcp_lms -> backend
nanobot gateway -> qwen-code-api -> Qwen
nanobot gateway -> mcp_webchat -> nanobot webchat UI relay -> browser
```

**Agent conversation:**
![Flutter chat](report-images/photo_2026-04-02_22-54-37.jpg)

**Status: PASS**

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
