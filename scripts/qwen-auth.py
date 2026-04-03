#!/usr/bin/env python3
"""Generate a fresh Qwen Code API key and update .env.docker.secret."""

import os
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_SECRET = ROOT / ".env.docker.secret"


def main() -> None:
    """Generate a new Qwen Code API key and update the secret file."""
    new_key = secrets.token_urlsafe(32)

    env_lines = []
    updated = False

    if ENV_SECRET.exists():
        for line in ENV_SECRET.read_text().splitlines():
            if line.startswith("QWEN_CODE_API_KEY="):
                env_lines.append(f"QWEN_CODE_API_KEY={new_key}")
                updated = True
            else:
                env_lines.append(line)

    if not updated:
        env_lines.append(f"QWEN_CODE_API_KEY={new_key}")

    ENV_SECRET.write_text("\n".join(env_lines) + "\n")
    print(f"Generated new QWEN_CODE_API_KEY: {new_key}")
    print(f"Updated {ENV_SECRET}")


if __name__ == "__main__":
    main()
