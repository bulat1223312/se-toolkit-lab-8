# Deploy and Document

The bot works locally via `--test` mode, but it's not a real product until it's running on the VM and responding in Telegram. In this task, you containerize the bot, add it to Docker Compose alongside the backend, and document how to deploy.

## Requirements targeted

- **P3.1** Bot containerized with Dockerfile
- **P3.2** Added as service in `docker-compose.yml`
- **P3.3** Deployed and running on VM
- **P3.4** README documents deployment

## Deliverables

### 1. Bot Dockerfile (`bot/Dockerfile`)

Installs dependencies from `bot/pyproject.toml` and runs the bot entry point.

### 2. Bot service in `docker-compose.yml`

Add a `bot` service to the existing compose file:
- Connects to backend via Docker network (service name, not `localhost`)
- Reads `BOT_TOKEN` and LLM credentials from environment
- Restarts unless stopped

### 3. Deployment verification

Bot container runs alongside the backend on your VM. Both are healthy.

### 4. README deploy section

Add a "Deploy" section explaining: required env vars, docker compose commands, how to verify.

## Verify

On your VM:

```terminal
cd ~/se-toolkit-lab-7
docker compose --env-file .env.docker.secret up --build -d
docker compose --env-file .env.docker.secret ps
```

You should see the bot service running alongside app, postgres, caddy. Then open Telegram and send `/start` to your bot — it should respond.

## Acceptance criteria

- [ ] Repo deployed at `~/se-toolkit-lab-7` on VM.
- [ ] `git remote get-url origin` matches student's GitHub repo.
- [ ] `docker-compose.yml` includes a bot service.
- [ ] Bot container running (`docker ps` shows it).
- [ ] Backend still healthy (`curl -sf http://localhost:42002/docs` returns 200).
- [ ] README has a section with "deploy" in heading.
- [ ] Bot responds in Telegram (TA-verified).

## Agent instructions

> Ask: "The bot needs to reach the backend inside Docker. Can it use `localhost`?" Then explain: Docker Compose creates a shared network where services reach each other by name (e.g., `http://app:8000`), not `localhost`. This is the one thing that trips everyone up in deployment.
