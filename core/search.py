"""YouTube video search by topic, sorted by view count with optional time filter."""

import base64

from scrapetube.scrapetube import get_videos

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

    raw = list(get_videos(url, api_endpoint, "contents", "videoRenderer", max_results, 1))

    videos = []
    for item in raw:
        video_id = item.get("videoId", "")
        title_runs = item.get("title", {}).get("runs", [{}])
        title = title_runs[0].get("text", "") if title_runs else ""
        channel_runs = item.get("ownerText", {}).get("runs", [{}])
        channel = channel_runs[0].get("text", "Unknown") if channel_runs else "Unknown"
        views = item.get("viewCountText", {}).get("simpleText", "N/A")
        duration = item.get("lengthText", {}).get("simpleText", "N/A")

        videos.append({
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "video_id": video_id,
            "views": views,
            "duration": duration,
            "channel": channel,
        })

    return videos
