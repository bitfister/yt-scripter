"""Fetch YouTube video transcripts (auto-generated or manual captions)."""

import json
import logging
import os
import time
from datetime import datetime, timezone

from youtube_transcript_api import YouTubeTranscriptApi

from config import MAX_TRANSCRIPT_CHARS, TRANSCRIPTS_DIR

logger = logging.getLogger("yt-scripter")

# Delay between transcript requests to avoid YouTube IP rate-limiting
REQUEST_DELAY = 2.0  # seconds


def _build_api() -> YouTubeTranscriptApi:
    """Build API client with Webshare proxy if credentials are set."""
    proxy_user = os.getenv("WEBSHARE_PROXY_USER")
    proxy_pass = os.getenv("WEBSHARE_PROXY_PASS")

    if proxy_user and proxy_pass:
        from youtube_transcript_api.proxies import WebshareProxyConfig
        logger.info("Using Webshare residential proxy (auto-rotating)")
        return YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username=proxy_user,
                proxy_password=proxy_pass,
            )
        )

    logger.info("No proxy configured — using direct connection")
    return YouTubeTranscriptApi()


# Single client instance — WebshareProxyConfig handles rotation + retry internally
_api = _build_api()


def _trim_at_sentence_boundary(text: str, max_chars: int) -> str:
    """Trim text to max_chars, cutting at the nearest sentence boundary."""
    if len(text) <= max_chars:
        return text
    # Find the last sentence-ending punctuation before the limit
    truncated = text[:max_chars]
    for sep in [". ", "! ", "? "]:
        last_idx = truncated.rfind(sep)
        if last_idx > max_chars * 0.7:  # Don't cut too aggressively
            return truncated[: last_idx + 1]
    # Fallback: cut at last space to avoid mid-word break
    last_space = truncated.rfind(" ")
    if last_space > max_chars * 0.8:
        return truncated[:last_space] + "..."
    return truncated + "..."


def get_transcript(video_id: str) -> str | None:
    """Fetch the transcript for a single video. Returns None if unavailable."""
    try:
        result = _api.fetch(video_id, languages=["en"])
        full_text = " ".join(s.text for s in result.snippets)
        return _trim_at_sentence_boundary(full_text, MAX_TRANSCRIPT_CHARS)
    except Exception as e:
        err_line = str(e).split("\n")[0]
        logger.info(f"No transcript for {video_id}: {err_line}")
        return None


def fetch_all_transcripts(videos: list[dict]) -> list[dict]:
    """Attach transcripts to each video dict. Skips videos without captions.

    Adds a delay between requests to avoid YouTube rate-limiting.
    Returns only videos that have transcripts.
    """
    results = []
    for i, video in enumerate(videos):
        if i > 0:
            time.sleep(REQUEST_DELAY)

        logger.info(f"Fetching transcript: {video['title'][:60]}...")
        transcript = get_transcript(video["video_id"])
        if transcript:
            video["transcript"] = transcript
            save_transcript(video)  # Auto-cache for future reuse
            results.append(video)

    logger.info(f"Got transcripts for {len(results)}/{len(videos)} videos")
    return results


# ---------- Transcript Cache ----------

def save_transcript(video: dict):
    """Save a video's transcript to the local cache for future reuse."""
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)
    video_id = video.get("video_id", "")
    if not video_id:
        return

    cache_data = {
        "video_id": video_id,
        "title": video.get("title", ""),
        "channel": video.get("channel", "Unknown"),
        "url": video.get("url", ""),
        "views": video.get("views", "N/A"),
        "duration": video.get("duration", "N/A"),
        "transcript": video.get("transcript", ""),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    path = os.path.join(TRANSCRIPTS_DIR, f"{video_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2)


def load_transcript(video_id: str) -> dict | None:
    """Load a cached transcript by video ID. Returns the full video dict or None."""
    path = os.path.join(TRANSCRIPTS_DIR, f"{video_id}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def list_cached_transcripts() -> list[dict]:
    """List all cached transcripts (metadata only, no full text).

    Returns list sorted by fetched_at descending (newest first).
    """
    if not os.path.isdir(TRANSCRIPTS_DIR):
        return []

    results = []
    for filename in os.listdir(TRANSCRIPTS_DIR):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(TRANSCRIPTS_DIR, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            results.append({
                "video_id": data.get("video_id", ""),
                "title": data.get("title", ""),
                "channel": data.get("channel", ""),
                "views": data.get("views", ""),
                "duration": data.get("duration", ""),
                "url": data.get("url", ""),
                "fetched_at": data.get("fetched_at", ""),
            })
        except (json.JSONDecodeError, OSError):
            continue

    results.sort(key=lambda x: x.get("fetched_at", ""), reverse=True)
    return results
