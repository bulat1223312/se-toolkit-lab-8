# Task 2 Fixes Summary

## Issues Fixed ✅

### 1. qwen-code-api crash on successful responses
**File:** `qwen-code-api/src/qwen_code_api/routes/chat.py`
**Problem:** `live_logger.proxy_response()` was called without the required `account_id` parameter
**Fix:** Added `account_id=None` to the function call (line 49)
**Error:** `TypeError: LiveLogger.proxy_response() missing 1 required positional argument: 'account_id'`

### 2. qwen-code-api couldn't read OAuth credentials
**File:** `docker-compose.yml`
**Problem:** Volume mount was `~/.qwen:/root/.qwen:ro` but container user is `nonroot` with home `/home/nonroot`
**Fix:** Changed to `~/.qwen:/home/nonroot/.qwen:ro`
**Error:** `RuntimeError: No credentials found. Authenticate with Qwen CLI first.`

### 3. Model name resolution
**File:** `qwen-code-api/src/qwen_code_api/models.py`
**Problem:** No alias for `coder-model` to the actual Qwen API model name
**Fix:** Added `"coder-model": "qwen3.5-plus"` to `MODEL_ALIASES`

### 4. Flutter client build and deployment
**Status:** ✅ Built successfully
- `client-web-flutter` container completed and wrote to Docker volume
- Caddy serves Flutter app at `/flutter`
- `main.dart.js` (2.4MB) is present and accessible
- HTML title: "Nanobot"

### 5. WebSocket route configuration
**Status:** ✅ Configured
- Caddy route `/ws/chat` → `http://nanobot:8765` is active
- webchat channel plugin installed and enabled
- MCP server `mcp_webchat` connected with 1 tool (mcp_webchat_ui_message)

## Remaining Issue ⚠️

### LLM OAuth Credentials Expired
**Problem:** The Qwen OAuth token has lost access to all models. Token refresh returns HTML (WAF challenge) instead of JSON.

**Symptoms:**
- qwen-code-api returns `400 Bad Request: model is not supported`
- nanobot logs show: `LLM returned error: Error: Internal Server Error`
- All model names tested fail: `qwen3.5-plus`, `qwen3-coder-plus`, `qwen-plus`, `qwen-max`, etc.

**Required Fix:**
```bash
# On the VM, re-authenticate with Qwen CLI:
qwen login
# Follow the OAuth flow in the browser to get fresh credentials

# Then restart the qwen-code-api service:
cd ~/se-toolkit-lab-8
docker compose --env-file .env.docker.secret restart qwen-code-api

# Verify:
curl -s http://localhost:42005/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: GRHecMYWt0m339m3pVhjywMyooNUVrMMpV6Zox9JvI4" \
  -d '{"model":"coder-model","messages":[{"role":"user","content":"Hello"}]}'
```

## Current Service Status

| Service | Status | Notes |
|---------|--------|-------|
| backend | ✅ Running | Healthy |
| postgres | ✅ Running | Healthy |
| caddy | ✅ Running | Serving /flutter, /ws/chat, /docs |
| qwen-code-api | ✅ Running | Healthy, but LLM calls fail due to OAuth |
| nanobot | ✅ Running | Gateway started, MCP servers connected |
| client-web-flutter | ✅ Completed | Build output in Docker volume |
| client-web-react | ✅ Running | Serving at / |
| victorialogs | ✅ Running | |
| victoriatraces | ✅ Running | |
| otel-collector | ✅ Running | |

## Verification Commands

```bash
# Flutter client
curl -s http://localhost:42002/flutter/ | grep "<title>"
# Expected: <title>Nanobot</title>

curl -s http://localhost:42002/flutter/main.dart.js | wc -c
# Expected: ~2.4MB

# Service status
docker compose --env-file .env.docker.secret ps

# Nanobot logs
docker compose --env-file .env.docker.secret logs nanobot --tail 50 | grep -E "MCP server|Agent loop|webchat"

# WebSocket test (after fixing LLM)
echo '{"content":"What labs are available?"}' | websocat "ws://localhost:42002/ws/chat?access_key=megakey1"
```

## Files Modified

1. `qwen-code-api/src/qwen_code_api/routes/chat.py` - Fixed `account_id` parameter
2. `qwen-code-api/src/qwen_code_api/models.py` - Added model alias
3. `docker-compose.yml` - Fixed volume mount path
4. `REPORT.md` - Updated with checkpoint evidence and LLM issue documentation
