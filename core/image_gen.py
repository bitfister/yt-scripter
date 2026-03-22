"""Generate scene images using DALL-E 3 API."""

import os
import requests

from openai import OpenAI

from config import OPENAI_API_KEY

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(_app_dir, "remotion", "public", "images")

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_scene_images(
    scenes: list[dict],
    topic: str,
    progress_callback=None,
) -> list[dict]:
    """Generate a DALL-E 3 image for each scene and save to remotion/public/images/.

    Adds an 'imagePath' field to each scene dict (relative path for Remotion import).

    Args:
        scenes: List of scene dicts (must have 'id', 'imagePrompt', 'mood').
        topic: The video topic for context.
        progress_callback: Optional callable(message: str) for progress updates.

    Returns:
        The scenes list with 'imagePath' added to each scene.
    """
    os.makedirs(IMAGES_DIR, exist_ok=True)

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

        # Skip if image already exists (avoid re-generating on retry)
        filename = f"{scene_id}.png"
        filepath = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(filepath):
            _progress(f"Using existing image for {scene.get('title', scene_id)}")
            scene["imagePath"] = f"images/{filename}"
            continue

        _progress(f"Generating image ({i + 1}/{len(scenes)}): {scene.get('title', scene_id)}")

        try:
            # Build the DALL-E prompt with style guidance
            full_prompt = (
                f"Cinematic wide-angle digital art for a YouTube video about '{topic}'. "
                f"Scene: {image_prompt}. "
                f"Style: Dark, moody, high contrast, volumetric lighting, "
                f"16:9 aspect ratio, no text or letters, no watermarks. "
                f"Color palette: deep blacks with {_mood_color_hint(scene.get('mood', 'dark'))} accents."
            )

            response = client.images.generate(
                model="dall-e-3",
                prompt=full_prompt,
                size="1792x1024",
                quality="standard",
                n=1,
            )

            image_url = response.data[0].url

            # Download and save
            img_data = requests.get(image_url, timeout=30).content
            filename = f"{scene_id}.png"
            filepath = os.path.join(IMAGES_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(img_data)

            # Relative path for Remotion (from src/ to public/)
            scene["imagePath"] = f"images/{filename}"
            _progress(f"Saved {filename}")

        except Exception as e:
            _progress(f"Image failed for {scene_id}: {e}")
            scene["imagePath"] = None

    return scenes


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
