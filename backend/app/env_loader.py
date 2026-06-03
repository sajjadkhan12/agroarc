"""
Load backend/.env from a fixed path (works in Docker and local dev).
"""

from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"


def load_backend_env() -> None:
    """Load backend/.env if present; env vars already set take precedence."""
    load_dotenv(ENV_FILE, override=False)
