"""Flask web UI for the YouTube Script Generator."""

import glob
import json
import logging
import os
import queue
import sys
import threading
import time
import zipfile
from io import BytesIO

# Ensure imports work regardless of CWD
_app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _app_dir)

from flask import (
    Flask, render_template, request, Response,
    session, redirect, url_for, send_file,
)
from werkzeug.security import check_password_hash

from config import MAX_VIDEOS, MAX_TOPIC_LENGTH

from core.search import search_videos, mark_videos_used
from core.transcript import fetch_all_transcripts, load_transcript, list_cached_transcripts
from core.summarize import summarize_video
from core.compile import compile_script
from core.trending import get_trending
from core.video_prompt import generate_remotion_prompt, REMOTION_PROMPT_TEMPLATE
from core.video_gen import generate_video_components
from core.image_gen import generate_scene_images
from core.tts_gen import generate_voiceover
from core.stock_media import fetch_stock_media
from cli import save_script

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(_app_dir, "app.log"), encoding="utf-8"),
    ],
)
logger = logging.getLogger("yt-scripter")

# --- Auth (from environment, with fallback for backward compat) ---
AUTH_USER = os.environ.get("AUTH_USER", "admin")
AUTH_HASH = os.environ.get(
    "AUTH_HASH",
    "scrypt:32768:8:1$57T8L6siHrHIxzmx$56532e145e46f52124758e3ab91f139eb94c4bb6dbf3b7c9f52cbbfca11d62c6848966ade9e04dc9d62f5580d51e0059afe14957a47ac3394e463c7ad2026c98",
)

# --- Flask app ---
app = Flask(__name__, template_folder=os.path.join(_app_dir, "templates"))

# Stable secret key: prefer env var, else generate-and-persist to a local file
_secret_key_path = os.path.join(_app_dir, ".flask_secret")
def _get_secret_key() -> bytes:
    env_key = os.environ.get("FLASK_SECRET_KEY")
    if env_key:
        return env_key.encode()
    if os.path.exists(_secret_key_path):
        return open(_secret_key_path, "rb").read()
    key = os.urandom(32)
    with open(_secret_key_path, "wb") as f:
        f.write(key)
    return key

app.secret_key = _get_secret_key()

# --- Progress queue management with auto-cleanup ---
_progress_queues: dict[int, queue.Queue] = {}
_queue_timestamps: dict[int, float] = {}  # Track creation time for cleanup
_next_id = 0
_lock = threading.Lock()

QUEUE_TTL = 900  # 15 minutes — auto-cleanup orphaned queues


def _new_queue() -> tuple[int, queue.Queue]:
    global _next_id
    with _lock:
        qid = _next_id
        _next_id += 1
        q = queue.Queue()
        _progress_queues[qid] = q
        _queue_timestamps[qid] = time.time()
    _cleanup_stale_queues()
    return qid, q


def _cleanup_stale_queues():
    """Remove queues older than QUEUE_TTL to prevent memory leaks."""
    now = time.time()
    with _lock:
        stale = [qid for qid, ts in _queue_timestamps.items() if now - ts > QUEUE_TTL]
        for qid in stale:
            _progress_queues.pop(qid, None)
            _queue_timestamps.pop(qid, None)
            logger.info(f"Cleaned up stale queue {qid}")


def _send(q: queue.Queue, event: str, data: dict):
    q.put(f"event: {event}\ndata: {json.dumps(data)}\n\n")


# --- Pipeline worker ---
def _pipeline_worker(topic: str, max_videos: int, time_range: str, q: queue.Queue,
                     selected_transcript_ids: list[str] | None = None,
                     style: str = "reporter"):
    """Run the pipeline in a background thread, pushing SSE events."""
    try:
        # Load locally-selected transcripts first
        local_videos = []
        if selected_transcript_ids:
            for vid_id in selected_transcript_ids:
                cached = load_transcript(vid_id)
                if cached:
                    local_videos.append(cached)
            if local_videos:
                _send(q, "progress", {
                    "step": 1,
                    "message": f"Loaded {len(local_videos)} saved transcript(s)",
                })

        # Calculate how many more we need from YouTube
        remaining = max(0, max_videos - len(local_videos))

        # Step 1: Search YouTube for remaining videos
        new_videos_with_transcripts = []
        if remaining > 0:
            time_label = f" (past {time_range})" if time_range != "any" else ""
            _send(q, "progress", {"step": 1, "message": f'Searching YouTube for "{topic}"{time_label}...'})
            videos = search_videos(topic, max_results=remaining, time_range=time_range)
            _send(q, "progress", {"step": 1, "message": f"Found {len(videos)} videos"})

            if not videos and not local_videos:
                _send(q, "error", {"message": "No videos found for this topic."})
                return

            # Step 2: Transcripts for new videos
            if videos:
                _send(q, "progress", {"step": 2, "message": "Fetching transcripts..."})
                new_videos_with_transcripts = fetch_all_transcripts(videos)
                _send(q, "progress", {
                    "step": 2,
                    "message": f"Got transcripts for {len(new_videos_with_transcripts)}/{len(videos)} videos",
                })

                # Mark new videos as used
                mark_videos_used(new_videos_with_transcripts)
        else:
            _send(q, "progress", {"step": 1, "message": "Using saved transcripts only — no YouTube search needed"})

        # Merge local + new
        videos_with_transcripts = local_videos + new_videos_with_transcripts

        if not videos_with_transcripts:
            _send(q, "error", {"message": "No transcripts available from any source."})
            return

        total = len(videos_with_transcripts)
        local_count = len(local_videos)
        new_count = len(new_videos_with_transcripts)
        _send(q, "progress", {
            "step": 2,
            "message": f"Total sources: {total} ({local_count} saved + {new_count} new)",
        })

        # Step 3: Summarize
        for i, video in enumerate(videos_with_transcripts, 1):
            title_display = video["title"][:50] + ("..." if len(video["title"]) > 50 else "")
            _send(q, "progress", {
                "step": 3,
                "message": f"Summarizing ({i}/{len(videos_with_transcripts)}): {title_display}",
            })
            video["summary"] = summarize_video(video["title"], video["transcript"])

        # Step 4: Compile
        _send(q, "progress", {"step": 4, "message": f"Compiling final script ({style} style) with Claude..."})
        script = compile_script(topic, videos_with_transcripts, style=style)

        # Save
        path = save_script(topic, script, videos_with_transcripts)

        sources = [
            {"title": v["title"], "url": v["url"], "channel": v["channel"], "views": v["views"]}
            for v in videos_with_transcripts
        ]
        _send(q, "done", {"script": script, "sources": sources, "saved_to": path})

    except Exception as e:
        logger.exception("Pipeline worker failed")
        _send(q, "error", {"message": str(e)})
    finally:
        _send(q, "end", {})


# --- Video generation worker ---
def _video_worker(script: str, topic: str, q: queue.Queue, voice: str = "onyx"):
    """Run full video generation pipeline: parse → images → stock → TTS → sync → components."""
    try:
        def on_progress(msg):
            _send(q, "progress", {"step": 1, "message": msg})

        # Step 1: Parse script into scenes with visual segments
        on_progress("Parsing script into visual scenes...")
        result = generate_remotion_prompt(script, topic)
        scene_data = result["scenes"]
        on_progress(f"Parsed {len(scene_data['scenes'])} scenes with visual segments")

        # Step 2: Generate DALL-E images for each scene
        on_progress("Generating AI images for scenes...")
        generate_scene_images(scene_data["scenes"], topic, progress_callback=on_progress)

        # Step 3: Fetch stock photos/videos from Pexels
        on_progress("Searching Pexels for stock media...")
        fetch_stock_media(scene_data["scenes"], progress_callback=on_progress)
        stock_count = sum(1 for s in scene_data["scenes"] if s.get("stockMedia"))
        on_progress(f"Stock media ready for {stock_count}/{len(scene_data['scenes'])} scenes")

        # Step 4: Generate voice-over audio (TTS)
        on_progress(f"Generating voice-over ({voice} voice)...")
        generate_voiceover(scene_data["scenes"], progress_callback=on_progress, voice=voice)

        # Step 5: Sync visual durations to actual audio length
        from mutagen.mp3 import MP3
        on_progress("Syncing visual timing to audio durations...")
        current_frame = 0
        for scene in scene_data["scenes"]:
            ap = scene.get("audioPath")
            if ap:
                mp3_path = os.path.join(_app_dir, "remotion", "public", ap)
                if os.path.exists(mp3_path):
                    try:
                        audio = MP3(mp3_path)
                        audio_seconds = audio.info.length
                        scene["audioDurationSeconds"] = round(audio_seconds, 2)
                        new_frames = int(audio_seconds * 30) + 6  # +0.2s buffer
                        old_frames = scene["durationFrames"]
                        if new_frames != old_frames:
                            scene["durationFrames"] = new_frames
                            if scene.get("segments") and old_frames > 0:
                                ratio = new_frames / old_frames
                                running = 0
                                for seg in scene["segments"]:
                                    seg["startOffset"] = int(running)
                                    seg["durationFrames"] = max(60, int(seg["durationFrames"] * ratio))
                                    running += seg["durationFrames"]
                    except Exception as e:
                        on_progress(f"Warning: could not sync {ap}: {e}")
            scene["startFrame"] = current_frame
            current_frame += scene["durationFrames"]
        scene_data["totalDurationFrames"] = current_frame
        on_progress(f"Synced — total video: {current_frame // 30}s")

        # Step 6: Save scene data with images + audio + synced durations
        data_dir = os.path.join(_app_dir, "remotion", "src", "data")
        os.makedirs(data_dir, exist_ok=True)
        with open(os.path.join(data_dir, "script.json"), "w", encoding="utf-8") as f:
            json.dump(scene_data, f, indent=2)

        # Step 7: Build prompt and generate Remotion components
        prompt = REMOTION_PROMPT_TEMPLATE.format(
            topic=topic,
            scenes_json=json.dumps(scene_data, indent=2),
        )
        on_progress("Generating Remotion components...")
        files = generate_video_components(prompt, progress_callback=on_progress)
        _send(q, "done", {"files": files})

    except Exception as e:
        logger.exception("Video worker failed")
        _send(q, "error", {"message": str(e)})
    finally:
        _send(q, "end", {})


# --- Routes ---

@app.before_request
def require_login():
    if request.endpoint not in ("login", "static") and not session.get("logged_in"):
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == AUTH_USER and check_password_hash(AUTH_HASH, password):
            session["logged_in"] = True
            return redirect(url_for("index"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def index():
    return render_template("index.html", max_videos=MAX_VIDEOS)


@app.route("/trending")
def trending():
    period = request.args.get("period", "today")
    category = request.args.get("category", "All")
    try:
        topics = get_trending(period=period, count=5, category=category)
        return {"topics": topics}
    except Exception as e:
        logger.warning(f"Trending fetch failed: {e}")
        return {"error": str(e)}, 500


@app.route("/last-result")
def last_result():
    """Return the most recent generated script so the UI can resume after a refresh."""
    output_dir = os.path.join(_app_dir, "output")
    files = sorted(glob.glob(os.path.join(output_dir, "*.md")), key=os.path.getmtime, reverse=True)
    if not files:
        return {"found": False}

    path = files[0]
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract topic from filename: Topic_Name_20260322_125905.md
    basename = os.path.splitext(os.path.basename(path))[0]
    topic = "_".join(basename.split("_")[:-2]).replace("_", " ")

    # Extract script (after "## Script\n")
    script = ""
    if "## Script" in content:
        script = content.split("## Script\n", 1)[-1].strip()

    # Extract sources
    sources = []
    if "## Sources" in content:
        src_block = content.split("## Sources\n", 1)[-1].split("\n---")[0].strip()
        for line in src_block.split("\n"):
            line = line.strip()
            if line.startswith("- ["):
                try:
                    title = line.split("[")[1].split("]")[0]
                    url = line.split("(")[1].split(")")[0]
                    rest = line.split("\u2014", 1)[-1].strip() if "\u2014" in line else ""
                    parts = rest.rsplit("(", 1)
                    channel = parts[0].strip() if len(parts) > 1 else ""
                    views = parts[1].rstrip(")") if len(parts) > 1 else ""
                    sources.append({"title": title, "url": url, "channel": channel, "views": views})
                except (IndexError, ValueError):
                    pass

    return {"found": True, "topic": topic, "script": script, "sources": sources, "saved_to": path}


@app.route("/video-prompt", methods=["POST"])
def video_prompt():
    data = request.json
    script = data.get("script", "").strip()
    topic = data.get("topic", "").strip()

    if not script:
        return {"error": "Script is required"}, 400

    try:
        result = generate_remotion_prompt(script, topic)

        # Save scene JSON to remotion/src/data/
        data_dir = os.path.join(_app_dir, "remotion", "src", "data")
        os.makedirs(data_dir, exist_ok=True)
        scene_path = os.path.join(data_dir, "script.json")
        with open(scene_path, "w", encoding="utf-8") as f:
            json.dump(result["scenes"], f, indent=2)

        return {
            "prompt": result["prompt"],
            "scenes": result["scenes"],
            "saved_to": scene_path,
        }
    except Exception as e:
        logger.exception("Video prompt generation failed")
        return {"error": str(e)}, 500


@app.route("/generate-video", methods=["POST"])
def generate_video():
    data = request.json
    script = data.get("script", "").strip()
    topic = data.get("topic", "").strip()
    voice = data.get("voice", "onyx")

    if not script or not topic:
        return {"error": "Script and topic are required"}, 400

    qid, q = _new_queue()
    thread = threading.Thread(target=_video_worker, args=(script, topic, q, voice), daemon=True)
    thread.start()

    return {"stream_id": qid}


def _voiceover_worker(q: queue.Queue):
    """Generate TTS audio for each scene in a background thread."""
    try:
        def on_progress(msg):
            _send(q, "progress", {"step": 1, "message": msg})

        # Load existing scene data
        scene_path = os.path.join(_app_dir, "remotion", "src", "data", "script.json")
        if not os.path.exists(scene_path):
            _send(q, "error", {"message": "No scene data found. Run Build Video first."})
            return

        with open(scene_path, "r", encoding="utf-8") as f:
            scene_data = json.load(f)

        scenes = scene_data.get("scenes", [])
        if not scenes:
            _send(q, "error", {"message": "Scene data has no scenes."})
            return

        # Generate audio for each scene
        on_progress(f"Generating voice-over for {len(scenes)} scenes...")
        generate_voiceover(scenes, progress_callback=on_progress)

        # Recalculate scene durations to match actual audio length using mutagen
        from mutagen.mp3 import MP3

        on_progress("Syncing visual timing to audio durations...")
        current_frame = 0
        for scene in scenes:
            ap = scene.get("audioPath")
            if ap:
                mp3_path = os.path.join(_app_dir, "remotion", "public", ap)
                if os.path.exists(mp3_path):
                    try:
                        audio = MP3(mp3_path)
                        audio_seconds = audio.info.length
                        scene["audioDurationSeconds"] = round(audio_seconds, 2)
                        new_frames = int(audio_seconds * 30) + 15  # +0.5s buffer
                        old_frames = scene["durationFrames"]

                        if new_frames != old_frames:
                            scene["durationFrames"] = new_frames
                            # Proportionally rescale segment timings
                            if scene.get("segments") and old_frames > 0:
                                ratio = new_frames / old_frames
                                running = 0
                                for seg in scene["segments"]:
                                    seg["startOffset"] = int(running)
                                    seg["durationFrames"] = max(60, int(seg["durationFrames"] * ratio))
                                    running += seg["durationFrames"]
                    except Exception as e:
                        on_progress(f"Warning: could not read {ap}: {e}")
            scene["startFrame"] = current_frame
            current_frame += scene["durationFrames"]
        scene_data["totalDurationFrames"] = current_frame
        on_progress(f"Synced — total video duration: {current_frame // 30}s ({current_frame} frames)")

        # Update scene data with audioPath fields and corrected durations
        with open(scene_path, "w", encoding="utf-8") as f:
            json.dump(scene_data, f, indent=2)

        audio_count = sum(1 for s in scenes if s.get("audioPath"))
        _send(q, "done", {"audio_count": audio_count})

    except Exception as e:
        _send(q, "error", {"message": str(e)})
    finally:
        _send(q, "end", {})


@app.route("/generate-voiceover", methods=["POST"])
def generate_voiceover_route():
    qid, q = _new_queue()
    thread = threading.Thread(target=_voiceover_worker, args=(q,), daemon=True)
    thread.start()
    return {"stream_id": qid}


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    topic = data.get("topic", "").strip()
    max_videos = int(data.get("max_videos", MAX_VIDEOS))
    time_range = data.get("time_range", "any")

    if not topic:
        return {"error": "Topic is required"}, 400

    # Input validation
    if len(topic) > MAX_TOPIC_LENGTH:
        return {"error": f"Topic too long (max {MAX_TOPIC_LENGTH} chars)"}, 400
    max_videos = max(1, min(max_videos, 20))

    selected_ids = data.get("selected_transcript_ids", [])
    style = data.get("style", "reporter")

    qid, q = _new_queue()
    thread = threading.Thread(
        target=_pipeline_worker,
        args=(topic, max_videos, time_range, q),
        kwargs={"selected_transcript_ids": selected_ids, "style": style},
        daemon=True,
    )
    thread.start()

    return {"stream_id": qid}


@app.route("/transcripts")
def list_transcripts():
    """List all cached transcripts (metadata only)."""
    return {"transcripts": list_cached_transcripts()}


@app.route("/stream/<int:stream_id>")
def stream(stream_id: int):
    q = _progress_queues.get(stream_id)
    if q is None:
        return {"error": "Invalid stream ID"}, 404

    def event_stream():
        try:
            while True:
                try:
                    msg = q.get(timeout=15)
                except queue.Empty:
                    yield ": keepalive\n\n"
                    continue
                yield msg
                if '"end"' in msg or "event: end" in msg:
                    break
        finally:
            # Always cleanup — handles both normal completion and client disconnect
            _progress_queues.pop(stream_id, None)
            _queue_timestamps.pop(stream_id, None)

    return Response(event_stream(), mimetype="text/event-stream")


@app.route("/download-remotion")
def download_remotion():
    """Serve generated Remotion files as a downloadable ZIP."""
    remotion_dir = os.path.join(_app_dir, "remotion")
    buf = BytesIO()

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Include src/ files (scenes, components, data)
        for root, _, files in os.walk(os.path.join(remotion_dir, "src")):
            for fname in files:
                fpath = os.path.join(root, fname)
                arcname = os.path.relpath(fpath, remotion_dir)
                zf.write(fpath, arcname)

        # Include public/images/
        img_dir = os.path.join(remotion_dir, "public", "images")
        if os.path.isdir(img_dir):
            for fname in os.listdir(img_dir):
                if fname.endswith((".png", ".jpg", ".jpeg", ".webp")):
                    fpath = os.path.join(img_dir, fname)
                    zf.write(fpath, os.path.join("public", "images", fname))

        # Include public/audio/
        audio_dir = os.path.join(remotion_dir, "public", "audio")
        if os.path.isdir(audio_dir):
            for fname in os.listdir(audio_dir):
                if fname.endswith((".mp3", ".wav", ".ogg")):
                    fpath = os.path.join(audio_dir, fname)
                    zf.write(fpath, os.path.join("public", "audio", fname))

        # Include public/stock/ (Pexels photos and videos)
        stock_dir = os.path.join(remotion_dir, "public", "stock")
        if os.path.isdir(stock_dir):
            for root, _, files in os.walk(stock_dir):
                for fname in files:
                    if fname.endswith((".jpg", ".png", ".mp4")):
                        fpath = os.path.join(root, fname)
                        arcname = os.path.relpath(fpath, remotion_dir)
                        zf.write(fpath, arcname)

    buf.seek(0)
    return send_file(buf, mimetype="application/zip", as_attachment=True, download_name="remotion-build.zip")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--ngrok", action="store_true", help="Expose via ngrok tunnel")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    if args.ngrok:
        from pyngrok import ngrok
        tunnel = ngrok.connect(args.port)
        print(f"\n{'='*50}")
        print(f"  Public URL: {tunnel.public_url}")
        print(f"{'='*50}\n")

    app.run(port=args.port, use_reloader=False)
