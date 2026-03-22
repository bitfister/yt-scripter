import os
from dotenv import load_dotenv

_config_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_config_dir, ".env"), override=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MODEL_FAST = "claude-haiku-4-5-20251001"  # Fast model for summarization and compilation
MAX_VIDEOS = 5
MAX_TRANSCRIPT_CHARS = 15000  # Trim long transcripts to stay within token limits
OUTPUT_DIR = os.path.join(_config_dir, "output")
