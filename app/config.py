import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]

load_dotenv(ROOT / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8080"))

APP_ENV = os.getenv("APP_ENV", "development")
ENABLE_MCP = os.getenv("ENABLE_MCP", "false").lower() == "true"

DATA_DIR = ROOT / "data"
AUDIT_DIR = DATA_DIR / "audit"
MEMORY_DIR = DATA_DIR / "memory"
EVALUATION_DIR = DATA_DIR / "evaluations"

for directory in [AUDIT_DIR, MEMORY_DIR, EVALUATION_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def validate_configuration(require_openai=True):
    if require_openai and not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to the .env file."
        )

    if not OPENAI_MODEL:
        raise RuntimeError("OPENAI_MODEL is not configured.")