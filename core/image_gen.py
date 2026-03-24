"""Generate scene images using DALL-E 3 API."""

import logging
import os
import time

import requests
from openai import OpenAI

from config import OPENAI_API_KEY, API_MAX_RETRIES, API_RETRY_BASE_DELAY

logger = logging.getLogger("yt-scripter")

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(_app_dir, "remotion", "public", "images")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def generate_scene_images(
    scenes: list[dict],
    topic: str,
    progress_callback=None,
) -> list[dict]:
    """Generate a DALL-E 3 image for each scene and save to remotion/public/images/.

    Adds an 'imagePath' field to each scene dict (relative path for Remotion's staticFile).
    Skips generation if the image already exists on disk (cache hit).

    Args:
        scenes: List of scene dicts (must have 'id', 'imagePrompt', 'mood').
        topic: The video topic for context.
        progress_callback: Optional callable(message: str) for progress updates.

    Returns:
        The scenes list with 'imagePath' added to each scene.
    """
    if not client:
        msg = "⚠ OPENAI_API_KEY not set — images will not be generated (gradient-only backgrounds)"
        if progress_callback:
            progress_callback(msg)
        logger.warning(msg)
        for scene in scenes:
            scene["imagePath"] = None
        return scenes

    os.makedirs(IMAGES_DIR, exist_ok=True)

    # Clear ALL old images — common IDs like hook/intro/outro collide across topics
    for existing in os.listdir(IMAGES_DIR):
        if existing.endswith(".png"):
            os.remove(os.path.join(IMAGES_DIR, existing))

    def _progress(msg: str):
        if progress_callback:
            progress_callback(msg)

    for i, scene in enumerate(scenes):
        scene_id = scene.get("id", f"scene-{i}")
        image_prompt = scene.get("imagePrompt", "")

        if not image_prompt:
            _progress(f"Skipping image for {scene_id} (no prompt)")
            scene["imagePath"] = None
            continue

        # Cache: skip if image already exists
        filename = f"{scene_id}.png"
        filepath = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(filepath):
            _progress(f"Using cached image for {scene.get('title', scene_id)}")
            scene["imagePath"] = f"images/{filename}"
            continue

        _progress(f"Generating image ({i + 1}/{len(scenes)}): {scene.get('title', scene_id)}")

        try:
            full_prompt = (
                f"Cinematic wide-angle digital art for a YouTube video about '{topic}'. "
                f"Scene: {image_prompt}. "
                f"Style: Dark, moody, high contrast, volumetric lighting, "
                f"16:9 aspect ratio, no text or letters, no watermarks. "
                f"Color palette: deep blacks with {_mood_color_hint(scene.get('mood', 'dark'))} accents."
            )

            image_url = _generate_with_retry(full_prompt, _progress)

            # Download and save
            img_data = requests.get(image_url, timeout=60).content
            with open(filepath, "wb") as f:
                f.write(img_data)

            scene["imagePath"] = f"images/{filename}"
            _progress(f"Saved {filename}")

        except Exception as e:
            logger.exception(f"Image generation failed for {scene_id}")
            _progress(f"Image failed for {scene_id}: {e}")
            scene["imagePath"] = None

    return scenes


def _generate_with_retry(prompt: str, progress_callback=None) -> str:
    """Call DALL-E 3 with exponential backoff retry. Returns image URL."""
    for attempt in range(1, API_MAX_RETRIES + 1):
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",
                quality="standard",
                n=1,
            )
            return response.data[0].url
        except Exception as e:
            if attempt == API_MAX_RETRIES:
                raise
            delay = API_RETRY_BASE_DELAY ** attempt
            logger.warning(f"DALL-E attempt {attempt} failed: {e}. Retrying in {delay}s...")
            if progress_callback:
                progress_callback(f"Image API error, retrying in {delay}s...")
            time.sleep(delay)


def _mood_color_hint(mood: str) -> str:
    """Map mood to color description for DALL-E prompt."""
    return {
        "tense": "red and orange",
        "calm": "blue and teal",
        "energetic": "orange and amber",
        "dark": "subtle gray and white",
        "warning": "red and yellow warning",
        "hopeful": "green and blue",
    }.get(mood, "orange and amber")
