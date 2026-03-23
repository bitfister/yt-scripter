"""YouTube video search by topic, sorted by view count with optional time filter."""

import base64
import json
import os

from scrapetube.scrapetube import get_videos

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USED_VIDEOS_PATH = os.path.join(_app_dir, "used_videos.json")

# YouTube protobuf-encoded sort values
_SORT_MAP = {"relevance": 1, "upload_date": 2, "view_count": 3, "rating": 4}

# Upload date filter values (0 = no filter)
_TIME_MAP = {"any": 0, "hour": 1, "today": 2, "week": 3, "month": 4, "year": 5}

VALID_TIME_RANGES = list(_TIME_MAP.keys())


def _build_sp(sort_by: str = "view_count", time_range: str = "any") -> str:
    """Build YouTube's sp parameter encoding sort, time filter, and type=video."""
    sort_val = _SORT_MAP[sort_by]
    time_val = _TIME_MAP[time_range]

    if time_val == 0:
        raw = bytes([8, sort_val, 18, 2, 16, 1])
    else:
        raw = bytes([8, sort_val, 18, 4, 8, time_val, 16, 1])

    return base64.b64encode(raw).decode().rstrip("=")


def search_videos(
    topic: str,
    max_results: int = 10,
    time_range: str = "any",
    sort_by: str = "view_count",
) -> list[dict]:
    """Search YouTube for videos on a topic.

    Args:
        topic: Search query.
        max_results: Max videos to return.
        time_range: One of "any", "hour", "today", "week", "month", "year".
        sort_by: One of "relevance", "upload_date", "view_count", "rating".

    Returns a list of dicts with keys: title, url, video_id, views, duration, channel.
    """
    sp = _build_sp(sort_by, time_range)
    url = f"https://www.youtube.com/results?search_query={topic}&sp={sp}"
    api_endpoint = "https://www.youtube.com/youtubei/v1/search"

    # Fetch more than needed so we can filter out previously used videos
    fetch_count = max_results * 3
    raw = list(get_videos(url, api_endpoint, "contents", "videoRenderer", fetch_count, 1))

    # Load previously used video IDs
    used_ids = _load_used_ids()

    videos = []
    for item in raw:
        video_id = item.get("videoId", "")
        title_runs = item.get("title", {}).get("runs", [{}])
        title = title_runs[0].get("text", "") if title_runs else ""
        channel_runs = item.get("ownerText", {}).get("runs", [{}])
        channel = channel_runs[0].get("text", "Unknown") if channel_runs else "Unknown"
        views = item.get("viewCountText", {}).get("simpleText", "N/A")
        duration = item.get("lengthText", {}).get("simpleText", "N/A")

        # Skip previously used videos
        if video_id in used_ids:
            continue

        videos.append({
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "video_id": video_id,
            "views": views,
            "duration": duration,
            "channel": channel,
        })

        if len(videos) >= max_results:
            break

    return videos


def mark_videos_used(videos: list[dict]):
    """Record video IDs as used so they won't appear in future searches."""
    used_ids = _load_used_ids()
    for v in videos:
        vid = v.get("video_id", "")
        if vid:
            used_ids.add(vid)
    _save_used_ids(used_ids)


def _load_used_ids() -> set:
    """Load the set of previously used video IDs from disk."""
    if os.path.exists(USED_VIDEOS_PATH):
        try:
            with open(USED_VIDEOS_PATH, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, TypeError):
            return set()
    return set()


def _save_used_ids(ids: set):
    """Persist the used video IDs to disk."""
    with open(USED_VIDEOS_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(ids), f, indent=2)
