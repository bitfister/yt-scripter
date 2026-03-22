"""Fetch YouTube video transcripts (auto-generated or manual captions)."""

import time
from youtube_transcript_api import YouTubeTranscriptApi
from config import MAX_TRANSCRIPT_CHARS

_api = YouTubeTranscriptApi()

# Delay between transcript requests to avoid YouTube IP rate-limiting
REQUEST_DELAY = 2.0  # seconds


def get_transcript(video_id: str) -> str | None:
    """Fetch the transcript for a single video. Returns None if unavailable."""
    try:
        result = _api.fetch(video_id, languages=["en"])
        full_text = " ".join(s.text for s in result.snippets)

        # Trim to stay within reasonable limits
        if len(full_text) > MAX_TRANSCRIPT_CHARS:
            full_text = full_text[:MAX_TRANSCRIPT_CHARS] + "..."

        return full_text

    except Exception as e:
        # Extract just the first line of the error for cleaner logging
        err_line = str(e).split("\n")[0]
        print(f"  [skip] No transcript for {video_id}: {err_line}")
        return None


def fetch_all_transcripts(videos: list[dict]) -> list[dict]:
    """Attach transcripts to each video dict. Skips videos without captions.

    Adds a delay between requests to avoid YouTube rate-limiting.
    Returns only videos that have transcripts.
    """
    results = []
    for i, video in enumerate(videos):
        # Delay between requests to avoid IP ban (skip delay for the first)
        if i > 0:
            time.sleep(REQUEST_DELAY)

        print(f"  Fetching transcript: {video['title'][:60]}...")
        transcript = get_transcript(video["video_id"])
        if transcript:
            video["transcript"] = transcript
            results.append(video)

    print(f"  Got transcripts for {len(results)}/{len(videos)} videos")
    return results
