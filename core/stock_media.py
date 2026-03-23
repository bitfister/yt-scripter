"""Fetch stock photos and videos from Pexels API for scene backgrounds."""

import logging
import os
import time

import requests

from config import PEXELS_API_KEY, API_MAX_RETRIES, API_RETRY_BASE_DELAY

logger = logging.getLogger("yt-scripter")

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOCK_DIR = os.path.join(_app_dir, "remotion", "public", "stock")

MAX_PHOTOS_PER_SCENE = 3
MAX_VIDEOS_PER_SCENE = 1
PEXELS_PHOTO_URL = "https://api.pexels.com/v1/search"
PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"
HEADERS = {"Authorization": PEXELS_API_KEY} if PEXELS_API_KEY else {}


def fetch_stock_media(
    scenes: list[dict],
    progress_callback=None,
) -> list[dict]:
    """Search Pexels and download stock photos/videos for each scene.

    Adds a 'stockMedia' list to each scene dict with entries:
      {"type": "photo"|"video", "path": "stock/{scene_id}/1.jpg", "query": "..."}

    Caches: skips download if the scene's stock directory already has files.

    Args:
        scenes: List of scene dicts (should have 'searchTerms' or 'title').
        progress_callback: Optional callable(message: str) for progress updates.

    Returns:
        The scenes list with 'stockMedia' added to each scene.
    """
    if not PEXELS_API_KEY:
        msg = "⚠ PEXELS_API_KEY not set — stock media will be skipped"
        if progress_callback:
            progress_callback(msg)
        logger.warning(msg)
        for scene in scenes:
            scene["stockMedia"] = []
        return scenes

    os.makedirs(STOCK_DIR, exist_ok=True)

    def _progress(msg: str):
        if progress_callback:
            progress_callback(msg)

    for i, scene in enumerate(scenes):
        scene_id = scene.get("id", f"scene-{i}")
        scene_dir = os.path.join(STOCK_DIR, scene_id)

        # Cache: skip if directory already has files
        if os.path.isdir(scene_dir) and any(
            f.endswith((".jpg", ".png", ".mp4")) for f in os.listdir(scene_dir)
        ):
            # Reconstruct stockMedia from existing files
            media = []
            for fname in sorted(os.listdir(scene_dir)):
                if fname.endswith((".jpg", ".png")):
                    media.append({"type": "photo", "path": f"stock/{scene_id}/{fname}", "query": "cached"})
                elif fname.endswith(".mp4"):
                    media.append({"type": "video", "path": f"stock/{scene_id}/{fname}", "query": "cached"})
            scene["stockMedia"] = media
            _progress(f"Using cached stock media for {scene.get('title', scene_id)}")
            continue

        # Build search query from searchTerms or title
        query = _build_query(scene)
        if not query:
            scene["stockMedia"] = []
            continue

        os.makedirs(scene_dir, exist_ok=True)
        media = []
        _progress(f"Fetching stock media ({i + 1}/{len(scenes)}): {scene.get('title', scene_id)}")

        # Fetch photos
        try:
            photos = _search_photos(query, per_page=MAX_PHOTOS_PER_SCENE)
            for j, photo in enumerate(photos):
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if not url:
                    continue
                fname = f"{j + 1}.jpg"
                dest = os.path.join(scene_dir, fname)
                _download_file(url, dest)
                media.append({"type": "photo", "path": f"stock/{scene_id}/{fname}", "query": query})
        except Exception as e:
            logger.warning(f"Pexels photo search failed for {scene_id}: {e}")

        # Fetch one video
        try:
            videos = _search_videos(query, per_page=MAX_VIDEOS_PER_SCENE)
            if videos:
                video_file = _pick_smallest_hd(videos[0])
                if video_file:
                    fname = "clip.mp4"
                    dest = os.path.join(scene_dir, fname)
                    _download_file(video_file["link"], dest)
                    media.append({"type": "video", "path": f"stock/{scene_id}/{fname}", "query": query})
        except Exception as e:
            logger.warning(f"Pexels video search failed for {scene_id}: {e}")

        scene["stockMedia"] = media
        _progress(f"Got {len([m for m in media if m['type'] == 'photo'])} photos + {len([m for m in media if m['type'] == 'video'])} videos for {scene_id}")

        # Rate limit courtesy: 1s between scenes
        if i < len(scenes) - 1:
            time.sleep(1)

    return scenes


def _build_query(scene: dict) -> str:
    """Build a Pexels search query from scene data."""
    terms = scene.get("searchTerms", [])
    if terms:
        return " ".join(terms[:3])
    # Fallback: use title words
    title = scene.get("title", "")
    return title


def _search_photos(query: str, per_page: int = 3) -> list[dict]:
    """Search Pexels photos API. Returns list of photo objects."""
    for attempt in range(1, API_MAX_RETRIES + 1):
        try:
            resp = requests.get(
                PEXELS_PHOTO_URL,
                headers=HEADERS,
                params={"query": query, "per_page": per_page, "orientation": "landscape"},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json().get("photos", [])
        except Exception as e:
            if attempt == API_MAX_RETRIES:
                raise
            time.sleep(API_RETRY_BASE_DELAY ** attempt)


def _search_videos(query: str, per_page: int = 1) -> list[dict]:
    """Search Pexels videos API. Returns list of video objects."""
    for attempt in range(1, API_MAX_RETRIES + 1):
        try:
            resp = requests.get(
                PEXELS_VIDEO_URL,
                headers=HEADERS,
                params={"query": query, "per_page": per_page, "orientation": "landscape"},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json().get("videos", [])
        except Exception as e:
            if attempt == API_MAX_RETRIES:
                raise
            time.sleep(API_RETRY_BASE_DELAY ** attempt)


def _pick_smallest_hd(video: dict) -> dict | None:
    """Pick the smallest HD-quality video file from Pexels video object."""
    files = video.get("video_files", [])
    hd_files = [f for f in files if f.get("quality") == "hd" and f.get("width", 0) >= 1280]
    if not hd_files:
        hd_files = [f for f in files if f.get("width", 0) >= 960]
    if not hd_files:
        return files[0] if files else None
    return min(hd_files, key=lambda f: f.get("file_size", float("inf")))


def _download_file(url: str, dest_path: str):
    """Download a file from URL to disk."""
    resp = requests.get(url, timeout=60, stream=True)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
