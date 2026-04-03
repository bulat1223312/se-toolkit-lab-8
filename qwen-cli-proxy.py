#!/usr/bin/env python3
"""Simple OpenAI-compatible API wrapper around qwen CLI using pty."""

import asyncio
import json
import os
import pty
import select
import signal
import time
import uuid
import sys
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
import fastapi

app = FastAPI(title="Qwen CLI Proxy")

API_KEY = "GRHecMYWt0m339m3pVhjywMyooNUVrMMpV6Zox9JvI4"


def run_qwen_cli_sync(prompt: str, timeout: int = 120) -> str:
    """Run qwen CLI synchronously using pty.fork and return the response."""
    import pty
    
    pid, fd = pty.fork()
    if pid == 0:
        # Child process
        os.execvp("qwen", ["qwen", "-p", prompt])
        os._exit(1)  # Should never reach here
    
    # Parent process - read output
    import select
    output = b""
    start = time.time()
    while True:
        elapsed = time.time() - start
        if elapsed > timeout:
            os.kill(pid, signal.SIGTERM)
            raise RuntimeError(f"qwen CLI timed out after {timeout}s")
        
        remaining = max(0.1, timeout - elapsed)
        ready, _, _ = select.select([fd], [], [], remaining)
        if ready:
            try:
                data = os.read(fd, 4096)
                if not data:
                    break
                output += data
            except OSError:
                break
    
    # Wait for child to finish
    try:
        _, status = os.waitpid(pid, 0)
        exit_code = os.WEXITSTATUS(status) if os.WIFEXITED(status) else 1
    except ChildProcessError:
        exit_code = 0
    
    response = output.decode("utf-8", errors="replace").strip()
    if not response:
        raise RuntimeError("qwen CLI returned empty response")
    if exit_code != 0:
        raise RuntimeError(f"qwen CLI failed (exit {exit_code}): {response[:500]}")
    return response


async def run_qwen_cli(prompt: str, timeout: int = 120) -> str:
    """Run qwen CLI asynchronously."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, run_qwen_cli_sync, prompt, timeout)


def validate_key(x_api_key: str | None, authorization: str | None) -> None:
    if not x_api_key and authorization:
        x_api_key = authorization.removeprefix("Bearer ").strip() if authorization.startswith("Bearer ") else authorization.strip()
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


@app.get("/v1/models")
async def list_models():
    return {"data": [{"id": "coder-model", "object": "model", "created": 1754686206, "owned_by": "qwen"}]}


@app.post("/v1/chat/completions")
async def chat_completions(
    request: fastapi.Request,
    x_api_key: str | None = Header(None),
    authorization: str | None = Header(None),
):
    validate_key(x_api_key, authorization)

    body: dict[str, Any] = await request.json()
    model = body.get("model", "coder-model")
    messages: list[dict[str, Any]] = body.get("messages", [])
    max_tokens = body.get("max_tokens", 8192)

    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Build prompt
    parts = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        parts.append(f"[{role}]: {content}")
    prompt = "\n".join(parts)

    try:
        response_text = await run_qwen_cli(prompt)
        latency_ms = int((time.time() - start_time) * 1000)

        return JSONResponse(content={
            "id": f"chatcmpl-{request_id}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": response_text},
                "finish_reason": "stop",
            }],
            "usage": {
                "prompt_tokens": len(prompt) // 4,
                "completion_tokens": len(response_text) // 4,
                "total_tokens": (len(prompt) + len(response_text)) // 4,
            },
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": {"message": str(e), "type": "cli_error"}},
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=42005)
