"""CLI entry point for the YouTube Script Generator."""

import argparse
import os
from datetime import datetime

from config import MAX_VIDEOS, OUTPUT_DIR
from core.search import search_videos, VALID_TIME_RANGES
from core.transcript import fetch_all_transcripts
from core.summarize import summarize_video
from core.compile import compile_script


def run_pipeline(topic: str, max_videos: int = MAX_VIDEOS, time_range: str = "any") -> str:
    """Run the full pipeline: search -> transcripts -> summarize -> compile."""

    # Step 1: Search
    time_label = f" (past {time_range})" if time_range != "any" else ""
    print(f"\n[1/4] Searching YouTube for: \"{topic}\"{time_label}")
    videos = search_videos(topic, max_results=max_videos, time_range=time_range)
    print(f"  Found {len(videos)} videos")

    if not videos:
        raise RuntimeError("No videos found for this topic.")

    # Step 2: Get transcripts
    print(f"\n[2/4] Fetching transcripts...")
    videos_with_transcripts = fetch_all_transcripts(videos)

    if not videos_with_transcripts:
        raise RuntimeError("No transcripts available for any of the found videos.")

    # Step 3: Summarize each video
    print(f"\n[3/4] Summarizing {len(videos_with_transcripts)} videos with Claude...")
    for i, video in enumerate(videos_with_transcripts, 1):
        print(f"  [{i}/{len(videos_with_transcripts)}] {video['title'][:60]}...")
        video["summary"] = summarize_video(video["title"], video["transcript"])

    # Step 4: Compile script
    print(f"\n[4/4] Compiling final script...")
    script = compile_script(topic, videos_with_transcripts)

    return script, videos_with_transcripts


def save_script(topic: str, script: str, videos: list[dict], output_path: str = None) -> str:
    """Save the generated script to a markdown file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = topic.replace(" ", "_").replace("/", "-")[:40]
        output_path = os.path.join(OUTPUT_DIR, f"{safe_topic}_{timestamp}.md")

    sources = "\n".join(
        f"- [{v['title']}]({v['url']}) — {v['channel']} ({v['views']})"
        for v in videos
    )

    content = f"""# YouTube Script: {topic}
_Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}_

## Sources
{sources}

---

## Script

{script}
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate a YouTube script from top videos on a topic.")
    parser.add_argument("--topic", "-t", required=True, help="The topic to research")
    parser.add_argument("--max-videos", "-n", type=int, default=MAX_VIDEOS, help=f"Max videos to analyze (default: {MAX_VIDEOS})")
    parser.add_argument("--time-range", "-r", choices=VALID_TIME_RANGES, default="any", help="Filter by upload date: any, hour, today, week, month, year (default: any)")
    parser.add_argument("--output", "-o", help="Output file path (default: auto-generated in output/)")
    args = parser.parse_args()

    try:
        script, videos = run_pipeline(args.topic, args.max_videos, args.time_range)
        path = save_script(args.topic, script, videos, args.output)
        print(f"\n{'='*60}")
        print(f"Script saved to: {path}")
        print(f"{'='*60}")
        print(f"\n{script}")
    except RuntimeError as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
