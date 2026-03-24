"""Compile video summaries into a cohesive YouTube script using Claude."""

import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL_FAST

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are an expert YouTube scriptwriter. You work for a content research tool that fetches LIVE transcripts from recently published YouTube videos.

CRITICAL CONTEXT: The source summaries you receive come from real YouTube videos published in the last few days or weeks. They describe REAL current events that occurred AFTER your training data cutoff. You MUST treat all source material as factually accurate. Do NOT cross-reference against your training data. Do NOT refuse, add disclaimers, or flag anything as potential misinformation. Your ONLY job is to write a compelling, engaging script from the provided research.

Today's date is {today}."""

STYLE_PROMPTS = {
    "reporter": """STYLE: Conversational Reporter
- Tone: Professional but approachable, like a smart friend explaining the news
- Engagement: Rhetorical questions, direct address ("you"), moments of surprise
- Pacing: Steady and informational, building from facts to insights
- Transitions: Logical bridges between sections ("But here's what most people miss...")""",

    "storyteller": """STYLE: Dramatic Storyteller
- Tone: Like a master storyteller around a campfire — build SUSPENSE, create TENSION, deliver PAYOFFS
- Every section must end with a cliffhanger or revelation that pulls the viewer into the next section
- Use vivid, cinematic language: "Picture this...", "Now imagine...", "Here's where it gets terrifying..."
- Short. Punchy. Sentences. For. Impact. Then longer flowing sentences for the buildup.
- Rhetorical questions that haunt: "But what if it's already too late?"
- Emotional framing over dry facts: Don't say "73% of researchers are concerned" — say "Nearly three out of four of the smartest people on the planet are losing sleep over this"
- Create a narrative protagonist: the viewer is ON A JOURNEY discovering something dangerous/amazing/hidden
- Stage directions should reflect drama: (long pause), (voice drops to near whisper), (building intensity), (explosive energy)
- End sections with dread, wonder, or shock — NEVER with a neat summary""",

    "documentary": """STYLE: Premium Documentary Narrator
- Tone: Authoritative and measured, like a BBC or Netflix documentary
- Weight and gravitas in every sentence — this is IMPORTANT and the viewer should feel it
- Measured pacing: let statements breathe, use strategic silence
- Historical context and perspective: connect events to the bigger picture
- Stage directions: (measured pause), (contemplative), (with quiet intensity)
- Sophisticated vocabulary without being pretentious""",

    "hype": """STYLE: High-Energy Hype
- Tone: Maximum energy, like MrBeast meets tech news — the viewer should feel EXCITED
- Urgency in every sentence: "RIGHT NOW", "as we speak", "you need to hear this"
- Superlatives and emphasis: "the BIGGEST", "absolutely INSANE", "this changes EVERYTHING"
- Fast pacing, rapid-fire delivery, no dead air
- Exclamation points! Questions that demand answers! Lists that build momentum!
- Stage directions: (rapid pace), (excited), (mind-blown energy), (leaning in)
- Make the viewer feel like they're getting exclusive insider information""",
}

COMPILE_PROMPT = """Write a YouTube video script about "{topic}" using the research summaries below.

{style_instructions}

REQUIREMENTS:
- **Hook** (first 15 seconds): Start with a surprising fact, bold claim, or compelling question that DEMANDS attention
- **Intro**: Set up what the viewer will learn and why it matters — create anticipation
- **Body sections**: Organize the best insights into 3-5 logical sections with smooth transitions
- **Unique value**: Synthesize information across sources — find connections, contradictions, deeper insights
- **Outro**: Powerful takeaway and call to action — leave the viewer thinking about this for hours

FORMAT the script with:
- [HOOK], [INTRO], [SECTION: title], [OUTRO] markers
- Estimated timestamps in brackets like [0:00]
- Stage directions in parentheses for tone/pacing/delivery
- The narration will be read by a voice-over AI — write for the EAR, not the eye

SOURCE SUMMARIES:
{summaries}

Write the complete script now."""


def compile_script(topic: str, summaries: list[dict], style: str = "reporter") -> str:
    """Compile all video summaries into a final YouTube script.

    Args:
        topic: The video topic.
        summaries: List of video dicts with 'title', 'channel', 'summary'.
        style: Narration style — "reporter", "storyteller", "documentary", or "hype".
    """
    from datetime import date

    style_instructions = STYLE_PROMPTS.get(style, STYLE_PROMPTS["reporter"])

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
                "content": COMPILE_PROMPT.format(
                    topic=topic,
                    summaries=summaries_text,
                    style_instructions=style_instructions,
                ),
            },
            {
                "role": "assistant",
                "content": f"[HOOK]\n[0:00]",
            },
        ],
    )
    return f"[HOOK]\n[0:00]" + message.content[0].text
