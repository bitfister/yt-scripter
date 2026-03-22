# YT Scripter — Project Context

Paste this file at the start of a new Claude Code session to restore full project context.

---

## What This Project Is

A YouTube research-to-script tool. Given a topic it:
1. Searches YouTube for top videos (via `scrapetube`)
2. Fetches their transcripts (`youtube-transcript-api`)
3. Summarizes each video with Claude Haiku
4. Compiles an original YouTube script with Claude Haiku
5. Optionally parses the script into a Remotion video scene spec

Available as both a **Flask web app** (with SSE real-time progress) and a **CLI**.

---

## File Map

```
app.py                  Flask server — SSE streaming, all HTTP endpoints
cli.py                  CLI entry: --topic, --max-videos, --time-range, --output
config.py               API keys, model names, MAX_VIDEOS, MAX_TRANSCRIPT_CHARS
requirements.txt        Python deps
.env                    ANTHROPIC_API_KEY (not committed)
Dockerfile              gunicorn, single worker, gthread, port 5000
deploy.sh               Lightsail Container Service deploy script

core/
  search.py             YouTube search via scrapetube, sorted by view count
  transcript.py         Transcript fetch, 2s delay between requests
  summarize.py          Per-video Claude Haiku summarization
  compile.py            Multi-source script compilation via Claude Haiku
  trending.py           Google Trends via trendspy (no API key needed)
  video_prompt.py       Script → scene JSON + Remotion skill prompt

templates/
  index.html            Single-page dark UI, SSE client, trending panel

remotion/               Remotion (React) video project — separate Node.js app
  src/data/script.json  Scene JSON written by /video-prompt endpoint
```

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.12, Flask 3.0 |
| LLM | Anthropic Claude API |
| Primary model | `claude-sonnet-4-20250514` (CLAUDE_MODEL) |
| Fast model | `claude-haiku-4-5-20251001` (CLAUDE_MODEL_FAST) — used for summarize + compile |
| YouTube search | scrapetube |
| Transcripts | youtube-transcript-api |
| Trends | trendspy |
| Video | Remotion 4 (React), Tailwind CSS 4 |
| Production server | gunicorn (gthread, 1 worker, 8 threads) |
| Hosting | AWS Lightsail Container Service |

---

## Key Config (config.py)

- `ANTHROPIC_API_KEY` — from `.env`
- `MAX_VIDEOS` = 5
- `MAX_TRANSCRIPT_CHARS` = 15,000
- Port default: 5000

---

## HTTP Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Web UI |
| POST | `/generate` | Start pipeline → returns `stream_id` |
| GET | `/stream/<id>` | SSE stream for that pipeline run |
| GET | `/trending` | Trending topics (`?period=today&category=All`) |
| POST | `/video-prompt` | Script → Remotion scene JSON + prompt |

---

## SSE Architecture (important for deployment)

- `/generate` starts a background thread, creates an in-memory `queue.Queue`, returns its ID
- `/stream/<id>` reads from that queue and yields SSE events
- **Queues are in-memory** → must use `--workers=1` in gunicorn; multiple workers would break streaming

---

## Running Locally

```bash
# Web app
python app.py --port 5050

# With ngrok tunnel
python app.py --port 5050 --ngrok

# CLI
python cli.py --topic "solar energy" --max-videos 5 --time-range month
```

---

## Deploying to Lightsail

```bash
export ANTHROPIC_API_KEY=sk-ant-...
chmod +x deploy.sh
./deploy.sh
```

`deploy.sh` builds the Docker image, creates a Lightsail container service (`nano`, ~$7/mo), pushes the image, and deploys with the API key as an env var. Prints the public URL on completion.

**Note:** The `output/` directory (saved scripts) is ephemeral inside the container — it resets on each deploy.

---

## Known Issues & Workarounds

- **YouTube IP rate-limiting:** Too many transcript requests → 429 blocks. 2s delay between requests is already in place. If blocked, wait a few hours.
- **Claude knowledge-cutoff refusals:** Summarize/compile use assistant prefill to prevent refusals about post-training events. Haiku is used instead of Sonnet because it's more instruction-following for this.
- **Stale Flask process:** If port is in use: `netstat -ano | grep ":5050"` → kill the PID.
- **Cookie auth:** `youtube-transcript-api` cookie auth is disabled in current version. If heavily rate-limited, proxy or YouTube Data API v3 would be the next step.
- **output/ not persistent on Lightsail:** Files saved by `save_script()` live only in the container. Would need S3 or Lightsail Object Storage to persist them across deploys.
