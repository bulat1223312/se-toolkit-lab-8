# Lab 8 — Report

## Task 2A — Deployed agent

**Nanobot startup logs:**
```
Using config: /app/nanobot/config.resolved.json
🐈 Starting nanobot gateway version 0.1.4.post6 on port 18790...
MCP server 'lms': connected, 9 tools registered
MCP server 'webchat': connected, 1 tools registered
Agent loop started
```

![Nanobot logs](report-images/Снимок%20экрана%202026-04-02%20224300.png)

**Status: PASS**

## Task 2B — Web client

**Flutter client:**
- URL: `http://10.93.25.49:42002/flutter`
- Flutter served at /flutter

**Agent conversation:**
![Flutter chat](report-images/photo_2026-04-02_22-54-37.jpg)

**WebSocket endpoint:**
- Endpoint: `ws://localhost:42002/ws/chat?access_key=megakey1`
- MCP server 'webchat': connected, 1 tool registered

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
