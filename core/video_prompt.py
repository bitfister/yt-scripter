"""Parse a generated script into structured scene data and produce a Remotion skill prompt."""

import json
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

PARSE_SYSTEM = """You are a video production assistant. You parse YouTube scripts into structured scene data for a React-based video framework (Remotion).

Given a script with [HOOK], [INTRO], [SECTION: title], [OUTRO] markers, timestamps, and stage directions in parentheses, you produce a JSON array of scenes.

Rules for timing:
- Narration pace: ~150 words per minute = ~2.5 words per second
- At 30fps, 1 second = 30 frames
- Calculate durationFrames from word count: ceil(wordCount / 2.5) * 30
- Add 60 extra frames (2 seconds) for scenes with (pause) stage directions
- Minimum scene duration: 90 frames (3 seconds)

Rules for visual cues:
- Extract all (parenthetical stage directions) as visual cues
- Identify key phrases: numbers, statistics, bold claims, proper nouns
- Assign a transition type: "cut" for high-energy scenes, "fade" for reflective/outro

Return ONLY valid JSON, no markdown fences."""

PARSE_PROMPT = """Parse this script into scene JSON. Return an array of scene objects.

Each scene object must have:
- "id": kebab-case identifier (e.g. "hook", "intro", "section-the-stealth-displacement")
- "type": one of "hook", "intro", "section", "outro"
- "title": display title for the scene
- "narration": the full narration text for this scene (no stage directions, no markers)
- "durationFrames": calculated from word count as described
- "visualCues": array of visual direction strings extracted from stage directions + inferred
- "keyPhrases": array of key phrases/stats to highlight visually (max 5 per scene)
- "transition": "cut" or "fade"

SCRIPT:
{script}"""

# The Remotion skill prompt template - this is what gets copy-pasted into Claude Code
REMOTION_PROMPT_TEMPLATE = """I need you to build a complete Remotion video composition for a YouTube video titled "{topic}".

## Scene Data
Here is the structured scene data (JSON). Use this as the source of truth for all content and timing:

```json
{scenes_json}
```

## Architecture
Build these files in `remotion/src/`:

1. **`data/script.json`** — Already saved (the JSON above)
2. **`ScriptVideo.tsx`** — Main composition component that imports scene data and renders scenes as `<Sequence>` blocks
3. **`scenes/HookScene.tsx`** — Bold, attention-grabbing kinetic typography
4. **`scenes/IntroScene.tsx`** — Clean intro with topic title and preview of what's covered
5. **`scenes/SectionScene.tsx`** — Content sections with text reveal and key phrase highlights
6. **`scenes/OutroScene.tsx`** — CTA with subscribe prompt and summary
7. **`components/AnimatedText.tsx`** — Reusable word-by-word or line-by-line text reveal
8. **`components/KeyPhrase.tsx`** — Highlighted stat/phrase with scale-up animation
9. **`components/SectionTitle.tsx`** — Slide-in lower-third title bar
10. **`Root.tsx`** — Update to register the composition with correct total duration and 1920x1080 resolution

## Visual Style
- **Resolution:** 1920×1080 at 30fps
- **Background:** Dark gradient (near-black to dark gray, e.g., `#0a0a0a` → `#1a1a1a`)
- **Primary text:** White (#ffffff), large sans-serif font (system-ui or Inter if available)
- **Accent color:** Vibrant orange-red (#ff4400) for highlights, key phrases, and progress elements
- **Secondary accent:** Warm amber (#ff8800) for section titles
- **Font sizes:** Hook text 64-80px, section narration 36-42px, key phrases 48-56px, section titles 28px

## Animation Patterns
Use these Remotion primitives:

### Hook Scene
- Dramatic text entrance: use `spring()` with `damping: 12, mass: 0.5` for scale-up from 0
- Key phrases appear one at a time with `interpolate(frame, [startFrame, startFrame+15], [0, 1])` for opacity
- Slight continuous zoom: `interpolate(frame, [0, durationInFrames], [1, 1.05])` on the background
- Text shadow/glow effect on accent-colored words

### Section Scenes
- Section title slides in from left using `spring()` for translateX, stays for 90 frames, then fades
- Narration text appears line-by-line (split by sentences), each line fading in with 20-frame stagger
- Key phrases get special treatment: scale up briefly to 1.1x with accent color, then settle back
- Subtle background gradient shift between sections for visual variety

### Intro Scene
- Topic title fades in centered, large
- Bullet points of "what you'll learn" slide in from right, staggered by 30 frames each
- Use the section titles from the scene data as the bullet points

### Outro Scene
- Key takeaway text centered with fade-in
- "Subscribe" CTA with pulsing animation using `spring()` with `config: {{ damping: 5 }}`
- Fade to black over last 60 frames

### Transitions
- Between scenes: 15-frame crossfade (overlap sequences by 15 frames, use opacity interpolation)
- "cut" transitions: no overlap, instant switch
- "fade" transitions: 30-frame overlap with opacity crossfade

## Component Details

### `ScriptVideo.tsx`
```
- Import scene data from './data/script.json'
- Calculate cumulative startFrame for each scene
- Render each scene inside <Sequence from={{startFrame}} durationInFrames={{scene.durationFrames}}>
- Pass scene data as props to the appropriate scene component based on scene.type
```

### `AnimatedText.tsx`
```
Props: {{ text: string, startFrame: number, style?: 'word-by-word' | 'line-by-line' | 'fade-in' }}
- Split text into units (words or sentences based on style)
- Each unit gets opacity interpolation: interpolate(frame - startFrame, [i * stagger, i * stagger + 15], [0, 1], {{ extrapolateRight: 'clamp' }})
- line-by-line: split on periods/newlines, 20-frame stagger
- word-by-word: split on spaces, 3-frame stagger (for hook impact)
```

### `KeyPhrase.tsx`
```
Props: {{ text: string, delay: number, color?: string }}
- Appears at delay frame with spring() scale from 0.8 to 1
- Brief 1.1x overshoot then settle
- Accent color background pill/highlight
- Large bold font
```

## Important Remotion Notes
- Use `useCurrentFrame()` and `useVideoConfig()` hooks
- All animations driven by frame number, not CSS animations
- Use `<AbsoluteFill>` for full-screen layouts
- Import spring from 'remotion': `import {{ spring, useCurrentFrame, useVideoConfig, interpolate, Sequence, AbsoluteFill }} from 'remotion'`
- Tailwind CSS is configured — you can use Tailwind classes
- Total composition duration = sum of all scene durationFrames (check the JSON)

Build all components now. Make sure the video tells a compelling visual story that matches the energy and pacing of the narration text."""


def parse_script_to_scenes(script: str, topic: str) -> list[dict]:
    """Use Claude to parse a generated script into structured scene data."""
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        system=PARSE_SYSTEM,
        messages=[
            {"role": "user", "content": PARSE_PROMPT.format(script=script)},
            {"role": "assistant", "content": "["},
        ],
    )
    raw = "[" + message.content[0].text
    # Strip any trailing markdown fences just in case
    raw = raw.strip().rstrip("`").strip()
    return json.loads(raw)


def generate_remotion_prompt(script: str, topic: str) -> dict:
    """Generate structured scene data and a Remotion skill prompt.

    Returns dict with:
      - scenes: list of scene dicts
      - prompt: ready-to-paste Remotion skill prompt string
    """
    scenes = parse_script_to_scenes(script, topic)

    # Calculate cumulative startFrame
    current_frame = 0
    total_frames = 0
    for scene in scenes:
        scene["startFrame"] = current_frame
        current_frame += scene["durationFrames"]
        total_frames += scene["durationFrames"]

    scene_data = {
        "topic": topic,
        "totalDurationFrames": total_frames,
        "fps": 30,
        "scenes": scenes,
    }

    prompt = REMOTION_PROMPT_TEMPLATE.format(
        topic=topic,
        scenes_json=json.dumps(scene_data, indent=2),
    )

    return {
        "scenes": scene_data,
        "prompt": prompt,
    }
