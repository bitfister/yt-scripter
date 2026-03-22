"""Generate voice-over audio for each scene using OpenAI TTS API."""

import logging
import os
import time

from openai import OpenAI

from config import OPENAI_API_KEY, API_MAX_RETRIES, API_RETRY_BASE_DELAY

logger = logging.getLogger("yt-scripter")

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(_app_dir, "remotion", "public", "audio")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# OpenAI TTS voices: alloy, echo, fable, onyx, nova, shimmer
DEFAULT_VOICE = "onyx"  # Deep, authoritative — good for documentary narration
DEFAULT_MODEL = "tts-1"  # Use "tts-1-hd" for higher quality (~2x cost)


def generate_voiceover(
    scenes: list[dict],
    progress_callback=None,
    voice: str = DEFAULT_VOICE,
) -> list[dict]:
    """Generate TTS audio for each scene and save to remotion/public/audio/.

    Adds an 'audioPath' field to each scene dict (relative path for Remotion's staticFile).
    Skips generation if the audio file already exists on disk (cache hit).

    Args:
        scenes: List of scene dicts (must have 'id' and 'narration').
        progress_callback: Optional callable(message: str) for progress updates.
        voice: OpenAI TTS voice name (default: onyx).

    Returns:
        The scenes list with 'audioPath' added to each scene.
    """
    if not client:
        msg = "⚠ OPENAI_API_KEY not set — voice-over will not be generated"
        if progress_callback:
            progress_callback(msg)
        logger.warning(msg)
        for scene in scenes:
            scene["audioPath"] = None
        return scenes

    os.makedirs(AUDIO_DIR, exist_ok=True)

    # Clear old audio files not matching current scene IDs
    current_ids = {s.get("id", f"scene-{i}") for i, s in enumerate(scenes)}
    for existing in os.listdir(AUDIO_DIR):
        if existing.endswith(".mp3"):
            stem = existing[:-4]
            if stem not in current_ids:
                os.remove(os.path.join(AUDIO_DIR, existing))

    def _progress(msg: str):
        if progress_callback:
            progress_callback(msg)

    for i, scene in enumerate(scenes):
        scene_id = scene.get("id", f"scene-{i}")
        narration = scene.get("narration", "").strip()

        if not narration:
            _progress(f"Skipping audio for {scene_id} (no narration)")
            scene["audioPath"] = None
            continue

        # Cache: skip if audio already exists
        filename = f"{scene_id}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(filepath):
            _progress(f"Using cached audio for {scene.get('title', scene_id)}")
            scene["audioPath"] = f"audio/{filename}"
            continue

        _progress(f"Generating audio ({i + 1}/{len(scenes)}): {scene.get('title', scene_id)}")

        try:
            _generate_with_retry(narration, filepath, voice, _progress)
            scene["audioPath"] = f"audio/{filename}"
            _progress(f"Saved {filename}")

        except Exception as e:
            logger.exception(f"TTS generation failed for {scene_id}")
            _progress(f"Audio failed for {scene_id}: {e}")
            scene["audioPath"] = None

    return scenes


def _generate_with_retry(
    text: str,
    output_path: str,
    voice: str,
    progress_callback=None,
):
    """Call OpenAI TTS with exponential backoff retry. Saves MP3 to output_path."""
    for attempt in range(1, API_MAX_RETRIES + 1):
        try:
            response = client.audio.speech.create(
                model=DEFAULT_MODEL,
                voice=voice,
                input=text,
            )
            response.stream_to_file(output_path)
            return
        except Exception as e:
            if attempt == API_MAX_RETRIES:
                raise
            delay = API_RETRY_BASE_DELAY ** attempt
            logger.warning(f"TTS attempt {attempt} failed: {e}. Retrying in {delay}s...")
            if progress_callback:
                progress_callback(f"TTS API error, retrying in {delay}s...")
            time.sleep(delay)
