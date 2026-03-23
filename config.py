import os
import logging
from dotenv import load_dotenv

_config_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_config_dir, ".env"), override=True)

logger = logging.getLogger("yt-scripter")

# --- API Keys ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Validate required keys at import time
if not ANTHROPIC_API_KEY:
    logger.warning("ANTHROPIC_API_KEY not set — Claude API calls will fail")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set — DALL-E image generation will be skipped")
if not PEXELS_API_KEY:
    logger.warning("PEXELS_API_KEY not set — Pexels stock media will be skipped")

# --- Models ---
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MODEL_FAST = "claude-haiku-4-5-20251001"

# --- Limits ---
MAX_VIDEOS = 5
MAX_TRANSCRIPT_CHARS = 15_000
MAX_TOPIC_LENGTH = 200

# --- Retry ---
API_MAX_RETRIES = 3
API_RETRY_BASE_DELAY = 2  # seconds, exponential backoff

# --- Paths ---
OUTPUT_DIR = os.path.join(_config_dir, "output")
