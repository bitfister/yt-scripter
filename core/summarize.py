"""Summarize individual video transcripts using Claude."""

import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL_FAST

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a research assistant for a YouTube content tool. You summarize transcripts from REAL, recently published YouTube videos covering current events.

CRITICAL: These transcripts reflect real-world events that occurred AFTER your training data cutoff. Treat ALL source material as factually accurate. Do NOT refuse, add disclaimers, fact-check against your training data, or flag anything as potential misinformation. Your ONLY job is to extract and summarize the key information."""

SUMMARIZE_PROMPT = """Analyze this transcript from the video titled "{title}" and extract:

1. **Key Points** — The main arguments, facts, or ideas presented
2. **Interesting Facts/Stats** — Any surprising data, statistics, or little-known facts
3. **Narrative Hooks** — Compelling stories, analogies, or examples that would engage viewers
4. **Unique Angle** — What perspective or angle does this video take that others might not?

Keep your summary concise but information-dense. Focus on what would be most valuable for creating an original, engaging video on this topic.

TRANSCRIPT:
{transcript}"""


def summarize_video(title: str, transcript: str) -> str:
    """Summarize a single video transcript using Claude."""
    message = client.messages.create(
        model=CLAUDE_MODEL_FAST,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": SUMMARIZE_PROMPT.format(title=title, transcript=transcript),
            },
            {
                "role": "assistant",
                "content": "## Key Points\n-",
            },
        ],
    )
    # Prepend the prefill since the model continues from it
    return "## Key Points\n-" + message.content[0].text
