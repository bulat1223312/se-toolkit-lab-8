# Plan and Scaffold

Before writing any feature code, you need a solid project structure and a plan. A well-scaffolded project makes everything easier: adding commands, testing, deploying. A bad structure means fighting the code at every step.

In this task, you use your coding agent to create a development plan and project skeleton.

## Requirements targeted

- **P0.1** Testable handler architecture — handlers work without Telegram
- **P0.2** CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout

## What you will build

A `bot/` directory inside your repo with an entry point, handler layer, configuration, dependencies, and a `--test` mode for offline verification.

```
se-toolkit-lab-7/
├── bot/                    ← NEW
│   ├── bot.py              ← entry point (Telegram startup + --test mode)
│   ├── handlers/           ← command handlers (no Telegram dependency)
│   ├── services/           ← API client, LLM client
│   ├── config.py           ← env var loading
│   ├── pyproject.toml    ← bot dependencies
│   └── PLAN.md             ← development plan
├── backend/                ← existing
├── frontend/               ← existing
└── docker-compose.yml      ← existing
```

The key idea is **testable handlers**: your command logic is just functions that take input and return text. They don't know about Telegram. The `--test` flag calls them directly, and later the Telegram bot calls the same functions. Same logic, different entry points.

## Test mode

The autochecker verifies the bot via `--test` — no Telegram connection needed:

```terminal
cd bot
uv run bot.py --test "/start"                    # → prints welcome message
uv run bot.py --test "/help"                     # → prints command list
uv run bot.py --test "/health"                   # → prints backend status
uv run bot.py --test "/scores lab-04"
uv run bot.py --test "what labs are available"    # Task 3
```

- Prints response to **stdout**, exits with code **0**
- Reads config from `.env.agent.secret` (`LMS_API_URL`, `LMS_API_KEY`, `LLM_API_KEY`)
- Does **not** connect to Telegram (no `BOT_TOKEN` needed in test mode)

## Deliverables

### 1. Development plan (`bot/PLAN.md`)

A plan produced with your coding agent. Describe the approach for all tasks: scaffold, backend integration, intent routing, deployment. At least 100 words.

### 2. Bot entry point (`bot/bot.py`)

Must support `--test` mode. Handlers can return placeholder text for now — real implementation comes in Task 2.

### 3. Handler directory (`bot/handlers/`)

Handler modules separated from the Telegram transport layer. The `--test` mode calls them directly without Telegram.

### 4. Dependencies (`bot/pyproject.toml`)

Bot-specific Python project with dependencies. `cd bot && uv sync` must work without errors.

### 5. Environment files

`.env.agent.example` must include `BOT_TOKEN`, `LMS_API_URL`, `LMS_API_KEY` with placeholder values. On the VM, `.env.agent.secret` must exist with real values filled in.

## Verify

Run this on your VM:

```terminal
cd ~/se-toolkit-lab-7/bot
uv sync
uv run bot.py --test "/start"
```

You should see a welcome message printed to the terminal. If it prints something and exits without errors — the scaffold works.

## Acceptance criteria

- [ ] `bot/PLAN.md` exists with at least 100 words.
- [ ] `bot/pyproject.toml` exists and `cd bot && uv sync` succeeds.
- [ ] `bot/handlers/` directory exists with at least one module.
- [ ] `cd bot && uv run bot.py --test "/start"` exits 0 with non-empty output.
- [ ] `.env.agent.secret` exists on the VM with `BOT_TOKEN`, `LMS_API_URL`, `LMS_API_KEY`.
- [ ] Repo is cloned at `~/se-toolkit-lab-7` on the VM.
- [ ] Git workflow followed (issue, branch, PR, review, merge).

## Agent instructions

> Ask: "Do you know what 'testable handler architecture' means?" The student likely doesn't — explain concisely: a handler is a function that takes input and returns a response. If it depends on Telegram, you can't test it without a running bot. As a plain function, you can call it from `--test` mode, from unit tests, or from Telegram — same logic, different entry points. Think of it like a web handler that works without a running HTTP server.
