# Deploy and Document

Deploy the bot on your VM alongside the backend and document the setup.

## What you will do

Add the bot as a Docker service in your existing `docker-compose.yml`, verify it responds in Telegram, and document the deployment.

## Deliverables

### 1. Bot Dockerfile (`bot/Dockerfile`)

A Dockerfile that builds and runs the bot. Should install dependencies from `bot/requirements.txt` and run the bot entry point.

### 2. Bot service in Docker Compose (`docker-compose.yml`)

Add a `bot` service to the existing `docker-compose.yml`. The bot should:
- Connect to the backend via Docker network (service name, not `localhost`)
- Read `BOT_TOKEN` and LLM credentials from environment
- Restart unless stopped

### 3. Deployment verification

The bot container runs alongside the backend on your VM. Both services are healthy.

### 4. README update

Add a "Deploy" section to the repo README explaining how to deploy the bot (env vars, docker compose, verification).

## Acceptance criteria

- [ ] `docker-compose.yml` includes a bot service.
- [ ] Bot container is running on the VM (`docker ps` shows it).
- [ ] Backend is still healthy alongside the bot (`curl -sf http://localhost:42002/docs` returns 200).
- [ ] `git remote get-url origin` on the VM matches the student's GitHub repo.
- [ ] README contains a section with "deploy" in the heading.
- [ ] Bot responds to messages in Telegram (TA-verified during demo).

## Working with your coding agent

> Explain multi-stage Docker builds. Why not just copy everything into one image?

> I need to add a `bot` service to my existing `docker-compose.yml`. The bot needs to reach the backend — explain Docker networking. Why can't I use `localhost` inside a container?

> The bot container starts but can't connect to the backend. Help me debug — what's the service name, what port, what's the network topology?

> Help me write the "Deploy" section of the README. A new developer should be able to deploy this from scratch by reading it.
