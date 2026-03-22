"""Fetch YouTube video transcripts (auto-generated or manual captions)."""

import logging
import os
import time

from youtube_transcript_api import YouTubeTranscriptApi

from config import MAX_TRANSCRIPT_CHARS

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
            results.append(video)

    logger.info(f"Got transcripts for {len(results)}/{len(videos)} videos")
    return results
