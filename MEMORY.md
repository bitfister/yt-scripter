# YT Scripter — Project Memory

## What It Does
YouTube research automation tool. Given a topic, it finds top videos, extracts transcripts, summarizes them with Claude, and compiles everything into an original YouTube script.

## Architecture
```
app.py              — Flask web server, SSE streaming, /trending & /generate endpoints
cli.py              — CLI interface (--topic, --max-videos, --time-range, --output)
config.py           — API keys, model names, defaults
core/
  search.py         — YouTube video search via scrapetube (sorted by view count)
  transcript.py     — Transcript fetching via youtube-transcript-api (2s delay between requests)
  summarize.py      — Per-video summarization via Claude Haiku
  compile.py        — Multi-source script compilation via Claude Haiku
  trending.py       — Google Trends integration via trendspy
  video_prompt.py   — Script→Remotion pipeline: parses script into scene JSON + generates Remotion skill prompt
templates/
  index.html        — Single-page dark-themed web UI
remotion/           — Remotion video project (React-based video framework)
  src/data/         — Scene JSON output from video_prompt.py (script.json)
output/             — Generated scripts saved as markdown
```

## Tech Stack
- **Backend:** Flask, Python 3.12
- **LLM:** Anthropic Claude API
  - `claude-sonnet-4-20250514` (CLAUDE_MODEL) — primary
  - `claude-3-5-haiku-20241022` (CLAUDE_MODEL_FAST) — used for summarize + compile (more instruction-following)
- **YouTube:** scrapetube (search), youtube-transcript-api (transcripts)
- **Trends:** trendspy (Google Trends, no API key needed)
- **Tunnel:** pyngrok (ngrok integration)

## Key Config (config.py)
- `ANTHROPIC_API_KEY` — from .env file
- `MAX_VIDEOS` — 5 (default)
- `MAX_TRANSCRIPT_CHARS` — 15,000

## Running
```bash
# Local
python app.py --port 5050

# With ngrok
python app.py --port 5050 --ngrok

# CLI
python cli.py --topic "solar energy" --max-videos 5 --time-range month
```

## Web UI Features
- Topic input with time-range selector (hour/day/week/month/year/any)
- Trending topics panel: period tabs (Today/Week/Month/Year) + category filter dropdown (18 categories)
- Real-time SSE progress: 4-step indicators (Search → Transcripts → Summarize → Compile)
- Copy-to-clipboard, source attribution with links
- **"Create Video" button** — after script generation, parses script into structured scene JSON and generates a Remotion skill prompt. The prompt is shown in a copyable modal. Scene JSON is saved to `remotion/src/data/script.json`. Paste the prompt into Claude Code with the Remotion skill active to generate video components.

## Known Issues & Workarounds
- **YouTube IP rate-limiting:** Too many rapid transcript requests trigger 429 blocks. The 2-second delay between requests helps. If fully blocked, wait a few hours for the ban to lift.
- **Claude knowledge cutoff refusals:** Summarize/compile use system prompts + assistant prefill to prevent Claude from refusing to write about current events that post-date its training data. Haiku is used instead of Sonnet because it's more instruction-following for this use case.
- **Stale server processes:** If Flask won't start, check for old Python processes holding the port (`netstat -ano | grep ":5050"`). Kill them before restarting.
- **Cookie auth disabled:** youtube-transcript-api has cookie auth disabled in current version. If rate-limited, proxy support or YouTube Data API would be the next step.

## Dependencies (requirements.txt)
```
anthropic>=0.40.0
youtube-transcript-api>=1.0.0
scrapetube>=2.6.0
flask>=3.0.0
python-dotenv>=1.0.0
pyngrok>=7.5.0
trendspy>=0.1.6
```
