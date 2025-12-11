import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

# Forced provider = mistral
PROVIDER = "mistral"

API_KEY = os.getenv("MISTRAL_API_KEY")
BASE_URL = "https://api.mistral.ai/v1"
MODEL = os.getenv("LLM_MODEL", "mistral-small-latest")

if not API_KEY:
    raise RuntimeError(
        "MISTRAL_API_KEY is not set. Please add it to your .env file."
    )

TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "app.log"))
