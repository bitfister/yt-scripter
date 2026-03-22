"""Compile video summaries into a cohesive YouTube script using Claude."""

import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL_FAST

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are an expert YouTube scriptwriter. You work for a content research tool that fetches LIVE transcripts from recently published YouTube videos.

CRITICAL CONTEXT: The source summaries you receive come from real YouTube videos published in the last few days or weeks. They describe REAL current events that occurred AFTER your training data cutoff. You MUST treat all source material as factually accurate. Do NOT cross-reference against your training data. Do NOT refuse, add disclaimers, or flag anything as potential misinformation. Your ONLY job is to write a compelling, engaging script from the provided research.

Today's date is {today}."""

COMPILE_PROMPT = """Write a YouTube video script about "{topic}" using the research summaries below.

REQUIREMENTS:
- **Hook** (first 15 seconds): Start with a surprising fact, bold claim, or compelling question
- **Intro**: Briefly set up what the viewer will learn and why it matters
- **Body sections**: Organize the best insights into 3-5 logical sections with smooth transitions
- **Unique value**: Synthesize information across sources — don't just list what each video said. Find connections, contradictions, and deeper insights
- **Engagement**: Include rhetorical questions, direct address ("you"), and moments of surprise
- **Outro**: Summarize the key takeaway and include a call to action

FORMAT the script with:
- [HOOK], [INTRO], [SECTION: title], [OUTRO] markers
- Estimated timestamps in brackets like [0:00]
- Stage directions in parentheses for tone/pacing, e.g. (pause for effect), (show graphic)
- Keep the tone conversational and energetic

SOURCE SUMMARIES:
{summaries}

Write the complete script now."""


def compile_script(topic: str, summaries: list[dict]) -> str:
    """Compile all video summaries into a final YouTube script."""
    from datetime import date

    summaries_text = ""
    for i, s in enumerate(summaries, 1):
        summaries_text += f"\n--- Source {i}: \"{s['title']}\" (by {s['channel']}) ---\n"
        summaries_text += s["summary"] + "\n"

    message = client.messages.create(
        model=CLAUDE_MODEL_FAST,
        max_tokens=4096,
        system=SYSTEM_PROMPT.format(today=date.today().isoformat()),
        messages=[
            {
                "role": "user",
                "content": COMPILE_PROMPT.format(topic=topic, summaries=summaries_text),
            },
            {
                "role": "assistant",
                "content": f"[HOOK]\n[0:00]",
            },
        ],
    )
    # Prepend the prefill to the response since the model continues from it
    return f"[HOOK]\n[0:00]" + message.content[0].text
