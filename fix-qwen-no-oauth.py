#!/usr/bin/env python3
"""Fix qwen-code-api to work without OAuth by using direct API key."""

import paramiko

VM_HOST = '10.93.25.49'
VM_USER = 'root'
VM_PASSWORD = '23112010A.z'

def run_cmd(ssh, cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    output = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    return exit_code, output, err

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(VM_HOST, username=VM_USER, password=VM_PASSWORD, timeout=60)

print("=" * 60)
print("ИСПРАВЛЕНИЕ QWEN-CODE-API ДЛЯ РАБОТЫ БЕЗ OAUTH")
print("=" * 60)

# Step 1: Read current chat.py
print("\n1. Чтение текущего chat.py:")
exit_code, output, err = run_cmd(ssh, "cat /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py")
print(output[:2000] if output else err)

# Step 2: Create fixed version
print("\n2. Создание исправленной версии chat.py:")
exit_code, output, err = run_cmd(ssh, '''
cat > /root/se-toolkit-lab-8/qwen-code-api/src/qwen_code_api/routes/chat.py << 'PYEOF'
"""POST /v1/chat/completions — proxy to DashScope with retry and streaming."""

import asyncio
import time
import uuid
from typing import Any

import httpx
from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse, StreamingResponse

from ..auth import AuthManager
from ..config import settings
from ..headers import build_headers
from ..logging_config import log
from ..models import (
    clamp_max_tokens,
    is_auth_error,
    is_quota_error,
    is_validation_error,
    make_error_response,
    resolve_model,
)
from ..utils.live_logger import live_logger

router = APIRouter()


async def _handle_regular(
    client: httpx.AsyncClient,
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    request_id: str,
    start_time: float,
) -> JSONResponse:
    resp = await client.post(url, json=payload, headers=headers)
    resp.raise_for_status()

    latency_ms = int((time.time() - start_time) * 1000)
    data = resp.json()
    input_tokens = data.get("usage", {}).get("prompt_tokens")
    output_tokens = data.get("usage", {}).get("completion_tokens")
    qwen_id = data.get("id")

    if settings.log_requests:
        live_logger.proxy_response(
            request_id=request_id,
            status_code=resp.status_code,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            qwen_id=qwen_id,
        )

    return JSONResponse(content=data)


async def _handle_streaming(
    client: httpx.AsyncClient,
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    request_id: str,
    start_time: float,
) -> StreamingResponse:
    async def event_generator():
        async with client.stream("POST", url, json=payload, headers=headers) as resp:
            resp.raise_for_status()
            async for chunk in resp.aiter_text():
                yield chunk

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/v1/chat/completions")
async def chat_completions(
    request: Request,
    x_api_key: str | None = Header(None),
    authorization: str | None = Header(None),
):
    from ..main import validate_api_key

    validate_api_key(x_api_key, authorization)

    body: dict[str, Any] = await request.json()
    model = resolve_model(body.get("model"))
    messages: list[dict[str, Any]] = body.get("messages", [])
    max_tokens = clamp_max_tokens(body.get("max_tokens"))
    is_streaming = body.get("stream", False)

    request_id = str(uuid.uuid4())
    start_time = time.time()
    token_count = sum(len(m.get("content", "")) for m in messages)

    live_logger.proxy_request(
        request_id=request_id,
        model=model,
        account_id=None,
        token_count=token_count,
        is_streaming=is_streaming,
    )

    # Determine URL and headers based on auth mode
    if settings.qwen_code_auth_use:
        # OAuth mode - use existing logic
        auth: AuthManager = request.app.state.auth
        access_token = await auth.get_valid_token(request.app.state.http_client)
        creds = auth.load_credentials()
        url = f"{auth.get_api_endpoint(creds)}/chat/completions"
        headers = build_headers(access_token, streaming=is_streaming)
    else:
        # Direct API key mode - use DashScope directly
        access_token = settings.qwen_code_api_key
        url = f"{settings.qwen_api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        if is_streaming:
            headers["Accept"] = "text/event-stream"

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": is_streaming,
        "temperature": body.get("temperature", 0.7),
        "max_tokens": max_tokens,
    }

    for field in ("top_p", "top_k", "repetition_penalty", "stop"):
        if field in body:
            payload[field] = body[field]

    if is_streaming:
        payload["stream_options"] = {"include_usage": True}

    last_error: Exception | None = None
    last_status: int | None = None
    for attempt in range(1, settings.max_retries + 1):
        try:
            if is_streaming:
                return await _handle_streaming(
                    request.app.state.http_client,
                    url,
                    payload,
                    headers,
                    request_id,
                    start_time,
                )
            else:
                return await _handle_regular(
                    request.app.state.http_client,
                    url,
                    payload,
                    headers,
                    request_id,
                    start_time,
                )
        except httpx.HTTPStatusError as e:
            last_status = e.response.status_code
            last_error = e
            error_message = e.response.text[:500] if e.response.text else str(e)

            if is_auth_error(last_status, error_message):
                if settings.qwen_code_auth_use:
                    try:
                        auth = request.app.state.auth
                        creds = auth.load_credentials()
                        if creds:
                            new_creds = await auth.refresh_token(creds, request.app.state.http_client)
                            continue
                    except Exception:
                        pass

                return JSONResponse(
                    status_code=last_status,
                    content=make_error_response(
                        message="Authentication failed. Please re-authenticate with Qwen CLI.",
                        error_type="authentication_error",
                    ),
                )

            if is_quota_error(last_status, error_message):
                return JSONResponse(
                    status_code=last_status,
                    content=make_error_response(
                        message="Quota exceeded. Please check your account.",
                        error_type="quota_error",
                    ),
                )

            if is_validation_error(last_status, error_message):
                return JSONResponse(
                    status_code=last_status,
                    content=make_error_response(
                        message=error_message,
                        error_type="validation_error",
                    ),
                )

            if attempt < settings.max_retries:
                await asyncio.sleep(settings.retry_delay_s * attempt)
                continue

    return JSONResponse(
        status_code=last_status or 500,
        content=make_error_response(
            message=str(last_error) if last_error else "Unknown error",
            error_type="proxy_error",
        ),
    )
PYEOF
echo "✅ chat.py updated"
''')
print(output if output else err)

# Step 3: Restart qwen-code-api
print("\n3. Перезапуск qwen-code-api:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret down qwen-code-api && docker compose --env-file .env.docker.secret up -d qwen-code-api")
print(output if output else err)

# Wait
print("\n4. Ожидание...")
run_cmd(ssh, "sleep 10")

# Step 4: Test health
print("\n5. Проверка health:")
exit_code, output, err = run_cmd(ssh, "curl -s http://localhost:42005/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:42005/health")
print(output if output else err)

# Step 5: Test chat
print("\n6. Тест chat endpoint:")
exit_code, api_key, _ = run_cmd(ssh, "grep '^QWEN_CODE_API_KEY=' /root/se-toolkit-lab-8/.env.docker.secret | cut -d= -f2")
exit_code, output, err = run_cmd(ssh, f'''
curl -s -X POST http://localhost:42005/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: {api_key.strip()}" \\
  -d '{{"model":"coder-model","messages":[{{"role":"user","content":"Hello, how are you?"}}],"max_tokens":100}}'
''', timeout=30)
print(output if output else err)

# Step 6: Restart nanobot
print("\n7. Перезапуск nanobot:")
exit_code, output, err = run_cmd(ssh, "cd /root/se-toolkit-lab-8 && docker compose --env-file .env.docker.secret restart nanobot")
print(output if output else err)

# Wait
print("\n8. Ожидание...")
run_cmd(ssh, "sleep 15")

# Step 7: Check nanobot logs
print("\n9. Логи nanobot:")
exit_code, output, err = run_cmd(ssh, "docker logs se-toolkit-lab-8-nanobot-1 2>&1 | grep -iE 'error|LLM|agent loop|Processing|Response' | tail -15")
print(output if output else err)

ssh.close()
print("\n" + "=" * 60)
print("ГОТОВО")
print("=" * 60)
