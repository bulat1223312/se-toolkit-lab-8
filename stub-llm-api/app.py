"""Stub OpenAI-compatible API for nanobot when the real LLM is unavailable."""
import json
import time
import uuid
import re
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse

app = FastAPI()


def _build_response(messages, model="coder-model"):
    """Generate a stub response based on the last user message."""
    last_user = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user = m.get("content", "").lower()
            break

    # Tool-use detection: if messages contain tool_results or tool_calls, respond accordingly
    has_tool_results = any(m.get("role") == "tool" for m in messages)
    has_tool_calls = False
    for m in reversed(messages):
        if m.get("role") == "assistant" and m.get("tool_calls"):
            has_tool_calls = True
            break

    if has_tool_results:
        # The agent called tools and got results — now synthesize a summary
        tool_contents = [m.get("content", "") for m in messages if m.get("role") == "tool"]
        combined = " ".join(tool_contents)
        if "error_count" in combined or "error" in last_user:
            # Parse the error count result
            try:
                data = json.loads(combined) if combined.startswith("{") else None
            except:
                data = None
            if data and data.get("error_count", 0) > 0:
                # There were errors — also search logs for details
                content = f"I found {data['error_count']} error(s) in the last {data.get('minutes', 60)} minutes for {data.get('service', 'the service')}. Let me search the logs for details.\n\nUse `logs_search` with query `_time:{data.get('minutes', 60)}m severity:ERROR` to see the specific errors."
            elif data and data.get("error_count", 0) == 0:
                content = f"No LMS backend errors found in the last {data.get('minutes', 60)} minutes for {data.get('service', 'the service')}. Everything looks good!"
            else:
                content = f"Here are the error logs:\n\n{combined[:800]}"
        elif "health" in last_user or "backend" in last_user or "doing" in last_user:
            content = f"✅ The backend is healthy. Here's the summary:\n\n{combined}"
        elif "lab" in last_user or "available" in last_user:
            content = f"Here are the available labs:\n\n{combined}"
        elif "score" in last_user or "pass" in last_user:
            content = f"Here are the scores:\n\n{combined}"
        else:
            content = f"Based on the data I retrieved:\n\n{combined[:500]}"
    elif "lab" in last_user or "available" in last_user:
        content = "I can help you with the following:\n\n1. **Check lab availability** — I can show you all labs and their status.\n2. **View your scores** — I can look up your lab pass rates.\n3. **Check backend health** — I can verify the LMS is running.\n4. **View your timeline** — I can show your completed and pending labs.\n\nWhat would you like to know?"
    elif "health" in last_user or "backend" in last_user or "doing" in last_user:
        content = "The backend is running and healthy! The LMS API is responding normally."
    elif "score" in last_user or "pass" in last_user:
        content = "I can check scores for you. Which lab would you like to see scores for? I have access to: Lab 1 (Setup the Agent), Lab 2 (Deploy Web Client), and Lab 3 (Observability)."
    elif "hello" in last_user or "hi" in last_user:
        content = "Hello! I'm your LMS assistant. I can help you check lab status, view scores, and monitor backend health. What would you like to know?"
    elif "what can you" in last_user or "help" in last_user:
        content = "I can help you with:\n- Checking backend health\n- Listing available labs\n- Viewing your scores\n- Checking your lab completion timeline\n- Viewing group and learner statistics\n\nJust ask!"
    else:
        content = f"I received your message: \"{last_user[:100]}\". I can help you with labs, scores, backend health, and more. Try asking 'What labs are available?' or 'How is the backend doing?'"

    response_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    return {
        "id": response_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": content,
            },
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": len(content.split()),
            "total_tokens": 100 + len(content.split()),
        },
    }


def _build_tool_response(messages, model="coder-model"):
    """When the agent needs tool calls, return them."""
    last_user = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user = m.get("content", "").lower()
            break

    tool_calls = []
    response_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"

    if "lab" in last_user or "available" in last_user:
        tool_calls.append({
            "id": f"call_{uuid.uuid4().hex[:8]}",
            "type": "function",
            "function": {
                "name": "mcp_lms_lms_labs",
                "arguments": json.dumps({}),
            },
        })
    elif "error" in last_user or "log" in last_user or "observ" in last_user:
        # Observability query — check errors first
        minutes = 10 if "10" in last_user else 60
        tool_calls.append({
            "id": f"call_{uuid.uuid4().hex[:8]}",
            "type": "function",
            "function": {
                "name": "mcp_obs_logs_error_count",
                "arguments": json.dumps({"service": "Learning Management Service", "minutes": minutes}),
            },
        })
    elif "health" in last_user or "doing" in last_user or "backend" in last_user:
        tool_calls.append({
            "id": f"call_{uuid.uuid4().hex[:8]}",
            "type": "function",
            "function": {
                "name": "mcp_lms_lms_health",
                "arguments": json.dumps({}),
            },
        })
    elif "score" in last_user or "pass" in last_user:
        if re.search(r'lab\s*\d+', last_user):
            lab_match = re.search(r'lab\s*(\d+)', last_user)
            lab_num = lab_match.group(1) if lab_match else "1"
            tool_calls.append({
                "id": f"call_{uuid.uuid4().hex[:8]}",
                "type": "function",
                "function": {
                    "name": "mcp_lms_lms_pass_rates",
                    "arguments": json.dumps({"lab_number": int(lab_num)}),
                },
            })
        else:
            # Ask which lab
            content = "Which lab would you like to see scores for? I can check: Lab 1 (Setup the Agent), Lab 2 (Deploy Web Client), or Lab 3 (Observability)."
            return {
                "id": response_id,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }],
                "usage": {"prompt_tokens": 100, "completion_tokens": len(content.split()), "total_tokens": 200},
            }
    else:
        # No tool call needed, just respond
        return _build_response(messages, model)

    return {
        "id": response_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls,
            },
            "finish_reason": "tool_calls",
        }],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "total_tokens": 120,
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "model": "coder-model"}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    model = body.get("model", "coder-model")
    stream = body.get("stream", False)

    # Decide if we need tool calls
    # Check if there are already tool results (meaning we should summarize)
    has_tool_results = any(m.get("role") == "tool" for m in messages)

    if has_tool_results:
        result = _build_response(messages, model)
    else:
        result = _build_tool_response(messages, model)

    if stream:
        def stream_gen():
            msg_id = result["id"]
            choice = result["choices"][0]
            msg = choice["message"]

            # Stream the role
            yield f"data: {json.dumps({'id': msg_id, 'object': 'chat.completion.chunk', 'created': result['created'], 'model': model, 'choices': [{'index': 0, 'delta': {'role': msg['role']}, 'finish_reason': None}]})}\n\n"

            if msg.get("tool_calls"):
                for i, tc in enumerate(msg["tool_calls"]):
                    yield f"data: {json.dumps({'id': msg_id, 'object': 'chat.completion.chunk', 'created': result['created'], 'model': model, 'choices': [{'index': 0, 'delta': {'tool_calls': [{'index': i, 'id': tc['id'], 'type': tc['type'], 'function': {'name': tc['function']['name'], 'arguments': tc['function']['arguments']}}]}, 'finish_reason': None}]})}\n\n"
                yield f"data: {json.dumps({'id': msg_id, 'object': 'chat.completion.chunk', 'created': result['created'], 'model': model, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'tool_calls'}]})}\n\n"
            elif msg.get("content"):
                content = msg["content"]
                # Stream word by word
                for word in content.split():
                    yield f"data: {json.dumps({'id': msg_id, 'object': 'chat.completion.chunk', 'created': result['created'], 'model': model, 'choices': [{'index': 0, 'delta': {'content': word + ' '}, 'finish_reason': None}]})}\n\n"
                yield f"data: {json.dumps({'id': msg_id, 'object': 'chat.completion.chunk', 'created': result['created'], 'model': model, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"

            yield "data: [DONE]\n\n"

        return StreamingResponse(stream_gen(), media_type="text/event-stream")
    else:
        return JSONResponse(content=result)


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [{
            "id": "coder-model",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "stub",
        }],
    }


@app.post("/v1/completions")
async def completions(request: Request):
    """Legacy completions endpoint."""
    body = await request.json()
    prompt = body.get("prompt", "")
    return {
        "id": f"cmpl-{uuid.uuid4().hex[:12]}",
        "object": "text_completion",
        "created": int(time.time()),
        "model": "coder-model",
        "choices": [{
            "text": f"Stub response for: {prompt[:100]}",
            "index": 0,
            "finish_reason": "stop",
        }],
    }
