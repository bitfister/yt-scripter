"""Flask web UI for the YouTube Script Generator."""

import json
import os
import queue
import sys
import threading

# Ensure imports work regardless of CWD
_app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _app_dir)

from flask import Flask, render_template, request, Response

from config import MAX_VIDEOS
from core.search import search_videos
from core.transcript import fetch_all_transcripts
from core.summarize import summarize_video
from core.compile import compile_script
from core.trending import get_trending
from core.video_prompt import generate_remotion_prompt
from cli import save_script

app = Flask(__name__, template_folder=os.path.join(_app_dir, "templates"))

# Per-request progress queues, keyed by a simple incrementing ID
_progress_queues: dict[int, queue.Queue] = {}
_next_id = 0
_lock = threading.Lock()


def _new_queue() -> tuple[int, queue.Queue]:
    global _next_id
    with _lock:
        qid = _next_id
        _next_id += 1
        q = queue.Queue()
        _progress_queues[qid] = q
    return qid, q


def _send(q: queue.Queue, event: str, data: dict):
    q.put(f"event: {event}\ndata: {json.dumps(data)}\n\n")


def _pipeline_worker(topic: str, max_videos: int, time_range: str, q: queue.Queue):
    """Run the pipeline in a background thread, pushing SSE events."""
    try:
        # Search
        time_label = f" (past {time_range})" if time_range != "any" else ""
        _send(q, "progress", {"step": 1, "message": f"Searching YouTube for \"{topic}\"{time_label}..."})
        videos = search_videos(topic, max_results=max_videos, time_range=time_range)
        _send(q, "progress", {"step": 1, "message": f"Found {len(videos)} videos"})

        if not videos:
            _send(q, "error", {"message": "No videos found for this topic."})
            return

        # Transcripts
        _send(q, "progress", {"step": 2, "message": "Fetching transcripts..."})
        videos_with_transcripts = fetch_all_transcripts(videos)
        _send(q, "progress", {"step": 2, "message": f"Got transcripts for {len(videos_with_transcripts)}/{len(videos)} videos"})

        if not videos_with_transcripts:
            _send(q, "error", {"message": "No transcripts available for any videos."})
            return

        # Summarize
        for i, video in enumerate(videos_with_transcripts, 1):
            _send(q, "progress", {
                "step": 3,
                "message": f"Summarizing ({i}/{len(videos_with_transcripts)}): {video['title'][:50]}...",
            })
            video["summary"] = summarize_video(video["title"], video["transcript"])

        # Compile
        _send(q, "progress", {"step": 4, "message": "Compiling final script with Claude..."})
        script = compile_script(topic, videos_with_transcripts)

        # Save
        path = save_script(topic, script, videos_with_transcripts)

        sources = [{"title": v["title"], "url": v["url"], "channel": v["channel"], "views": v["views"]} for v in videos_with_transcripts]
        _send(q, "done", {"script": script, "sources": sources, "saved_to": path})

    except Exception as e:
        _send(q, "error", {"message": str(e)})
    finally:
        _send(q, "end", {})


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
        return {"error": str(e)}, 500


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
        return {"error": str(e)}, 500


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    topic = data.get("topic", "").strip()
    max_videos = int(data.get("max_videos", MAX_VIDEOS))
    time_range = data.get("time_range", "any")

    if not topic:
        return {"error": "Topic is required"}, 400

    qid, q = _new_queue()
    thread = threading.Thread(target=_pipeline_worker, args=(topic, max_videos, time_range, q), daemon=True)
    thread.start()

    return {"stream_id": qid}


@app.route("/stream/<int:stream_id>")
def stream(stream_id: int):
    q = _progress_queues.get(stream_id)
    if q is None:
        return {"error": "Invalid stream ID"}, 404

    def event_stream():
        while True:
            msg = q.get()
            yield msg
            if '"end"' in msg or "event: end" in msg:
                break
        # Cleanup
        _progress_queues.pop(stream_id, None)

    return Response(event_stream(), mimetype="text/event-stream")


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
