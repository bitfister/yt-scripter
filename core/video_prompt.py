"""Parse a generated script into structured scene data with visual segments and produce a Remotion composition prompt."""

import json
import re
import anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ---------- Scene Parsing ----------

PARSE_SYSTEM = """You are a video production director. You transform YouTube scripts into structured scene data for a motion graphics video framework (Remotion).

The video is a VISUAL COMPANION to voice-over narration. The narration will be read aloud as audio — it is NEVER displayed on screen as text paragraphs.

Your job is to decide WHAT VISUALS should appear on screen to illustrate each part of the narration.

## Rules for scenes
- Break the script into scenes using [HOOK], [INTRO], [SECTION: title], [OUTRO] markers
- Each scene gets a mood, accent color, and DALL-E image prompt
- Calculate durationFrames from narration word count: ceil(wordCount / 2.5) * 30

## Rules for segments (the core visual decisions)
- Break each scene into 3-8 visual segments
- Each segment is ONE visual beat — what the viewer sees for 7-20 seconds
- Segment durations should sum to approximately the scene durationFrames
- Each segment has exactly one visualType from the catalog below

## Visual Type Catalog

| visualType | Required fields | Use for |
|---|---|---|
| headline | headline (max 10 words) | Opening a scene, key thesis statements |
| stat_highlight | value, label, emphasis ("normal"/"danger"/"success") | Statistics, numbers, percentages |
| comparison | leftLabel, rightLabel, leftItems[], rightItems[] | Before/after, this vs that, pros vs cons |
| timeline | events[{label, year?}] | Chronological events, predictions, progression |
| icon_list | title, items[] (max 6 items) | Lists of features, factors, categories |
| quote | text (max 20 words), attribution? | Powerful statements, expert quotes |
| warning | text (max 8 words), severity ("caution"/"danger"/"critical") | Alarms, alerts, urgent messages |
| reveal | value, label | Dramatic single-stat full-screen reveal |

## Rules for imagePrompt
- Describe a cinematic visual scene that captures the emotional essence of this scene
- Focus on atmosphere, objects, lighting — NOT text or UI elements
- Example: "A humanoid robot in a dark laboratory, its face split between friendly smile and cold mechanical interior, dramatic side lighting"

Return ONLY valid JSON, no markdown fences."""

PARSE_PROMPT = """Parse this script into scenes with visual segments.

Return an array of scene objects. Each scene must have:
- "id": kebab-case (e.g. "hook", "section-the-timeline")
- "type": "hook" | "intro" | "section" | "outro"
- "title": display title
- "durationFrames": calculated from narration word count
- "transition": "cut" or "fade"
- "mood": "tense" | "calm" | "energetic" | "dark" | "warning" | "hopeful"
- "colorAccent": hex color that fits the mood (e.g. "#ff4400" for tense, "#44aaff" for calm)
- "imagePrompt": cinematic image description for DALL-E (scene atmosphere, no text)
- "narration": full narration text (for voice-over, NEVER displayed on screen)
- "segments": array of visual segments, each with:
  - "startOffset": frames from scene start
  - "durationFrames": 200-600 frames (7-20 seconds)
  - "visualType": one from the catalog
  - Plus the required fields for that visualType

Example segment for a statistic:
{{"startOffset": 300, "durationFrames": 400, "visualType": "stat_highlight", "value": "73%", "label": "of researchers surveyed express concern", "emphasis": "danger"}}

Example segment for a comparison:
{{"startOffset": 700, "durationFrames": 500, "visualType": "comparison", "leftLabel": "Before", "rightLabel": "After", "leftItems": ["Manual process", "3 days"], "rightItems": ["Automated", "3 minutes"]}}

SCRIPT:
{script}"""


# ---------- Remotion Composition Prompt ----------

REMOTION_PROMPT_TEMPLATE = """Build a Remotion video composition for "{topic}".

## Scene Data
```json
{scenes_json}
```

## Pre-Built Component Library
These components ALREADY exist in `../components/`. Import them from '../components'. Do NOT rewrite or modify them.

### Available Components & Props:

**ParticleField** — Animated floating particle background
  Props: count?, color?, speed?, opacity?, maxSize?, direction? ('up'|'down'|'random')

**GradientBackground** — Mood-driven animated gradient with accent glow
  Props: mood? ('tense'|'calm'|'energetic'|'dark'|'warning'|'hopeful'), colorAccent?, animationIntensity? ('low'|'medium'|'high')

**AnimatedCounter** — Number counting up with spring easing
  Props: from?, to (number), startFrame?, durationFrames?, format? ('number'|'percent'|'currency'|'multiplier'), suffix?, prefix?, color?, fontSize?

**StatHighlight** — Big statistic value with label, animated entrance
  Props: value (string), label (string), emphasis? ('normal'|'danger'|'success'), startFrame?, durationFrames?, color?

**ComparisonLayout** — Two-column side-by-side comparison
  Props: leftLabel, rightLabel, leftItems[], rightItems[], startFrame?, style? ('side-by-side'|'versus'), leftColor?, rightColor?

**TimelineBar** — Animated timeline with sequential event dots
  Props: events ({{label, year?}}[]), startFrame?, orientation? ('horizontal'|'vertical'), color?

**IconGrid** — Items appearing in staggered grid with monogram icons
  Props: title?, items (string[]), startFrame?, columns? (2|3|4), iconStyle? ('circle'|'pill'|'card'), color?

**QuoteCard** — Styled quote with typewriter reveal effect
  Props: text, attribution?, startFrame?, style? ('elegant'|'bold'|'warning'), color?

**WarningBanner** — Alert banner with hazard stripes and optional screen shake
  Props: text, startFrame?, durationFrames?, severity? ('caution'|'danger'|'critical'), color?

**LowerThird** — Broadcast-style title bar overlay
  Props: title, subtitle?, startFrame?, durationFrames?, position? ('left'|'center'), accentColor?

**KineticHeadline** — Large kinetic text (MAX 10 WORDS), auto-sized
  Props: text, startFrame?, durationFrames?, style? ('impact'|'elegant'|'glitch'), color?, fontSize?

**ProgressBar** — Thin video progress indicator
  Props: color?, position? ('top'|'bottom'), height?

## Background Images
Each scene has a DALL-E generated background image. Use Remotion's `staticFile()` to load them:
```tsx
import {{ Img, staticFile }} from 'remotion';
// In the scene component:
<Img src={{staticFile(scene.imagePath)}} style={{...}} />
```
If `scene.imagePath` is null, fall back to GradientBackground only.

## Files to Create

1. **`ScriptVideo.tsx`** — Main composition
   - Import scene data from './data/script.json'
   - Render each scene inside `<Sequence from={{scene.startFrame}} durationInFrames={{scene.durationFrames}}>`
   - Include `<ProgressBar />` across the full video
   - Route to the correct scene component by `scene.type`

2. **`scenes/HookScene.tsx`** — Attention-grabbing opening
   - Background: image (with slow Ken Burns zoom) + GradientBackground overlay (opacity 0.6) + ParticleField
   - Render segments using library components
   - Use WarningBanner or KineticHeadline with 'glitch' style for maximum impact

3. **`scenes/IntroScene.tsx`** — Topic intro with preview
   - Background: image + gradient overlay + particles
   - LowerThird with topic title
   - IconGrid showing what sections will cover (use section titles from scene data)

4. **`scenes/SectionScene.tsx`** — Content sections (most important - handles all section scenes)
   - Background: image (Ken Burns pan/zoom) + GradientBackground overlay + ParticleField
   - Read `scene.segments` array and render EACH segment inside a `<Sequence>`:
   ```tsx
   {{scene.segments.map(seg => (
     <Sequence key={{seg.startOffset}} from={{seg.startOffset}} durationInFrames={{seg.durationFrames}}>
       {{seg.visualType === 'stat_highlight' && <StatHighlight value={{seg.value}} label={{seg.label}} emphasis={{seg.emphasis}} />}}
       {{seg.visualType === 'comparison' && <ComparisonLayout leftLabel={{seg.leftLabel}} ... />}}
       {{seg.visualType === 'timeline' && <TimelineBar events={{seg.events}} />}}
       {{seg.visualType === 'headline' && <KineticHeadline text={{seg.headline}} />}}
       {{seg.visualType === 'icon_list' && <IconGrid title={{seg.title}} items={{seg.items}} />}}
       {{seg.visualType === 'quote' && <QuoteCard text={{seg.text}} attribution={{seg.attribution}} />}}
       {{seg.visualType === 'warning' && <WarningBanner text={{seg.text}} severity={{seg.severity}} />}}
       {{seg.visualType === 'reveal' && <StatHighlight value={{seg.value}} label={{seg.label}} emphasis="danger" />}}
     </Sequence>
   ))}}
   ```
   - Add LowerThird with scene title at the beginning of each section

5. **`scenes/OutroScene.tsx`** — Closing with CTA
   - Background: image + gradient + particles
   - QuoteCard with key takeaway
   - KineticHeadline with call-to-action
   - Fade to black over last 60 frames

6. **`Root.tsx`** — Register composition
   - Import ScriptVideo, set 1920x1080 at 30fps
   - Set durationInFrames from scriptData.totalDurationFrames

## Voice-Over Audio
If a scene has an `audioPath` field, add voice-over audio to that scene:
```tsx
import {{ Audio, staticFile }} from 'remotion';
// Inside each scene's Sequence in ScriptVideo.tsx:
{{scene.audioPath && <Audio src={{staticFile(scene.audioPath)}} />}}
```
Add this audio element inside each scene's `<Sequence>` in `ScriptVideo.tsx`, NOT in individual scene components.

## CRITICAL VISUAL RULES
1. NEVER display narration text on screen. Narration is for voice-over ONLY.
2. On-screen text: ONLY headlines (max 10 words), stat values, labels, and short titles.
3. EVERY scene must have: background image (or gradient fallback) + ParticleField for depth.
4. Use scene.mood and scene.colorAccent to configure GradientBackground and component colors.
5. Ken Burns effect on background images: slow zoom (1.0 → 1.08) or slow pan using interpolate.
6. Visual layering order: image bg → gradient overlay (0.5-0.7 opacity) → particles → main content → LowerThird.
7. Import `Sequence`, `useCurrentFrame`, `interpolate`, `Img`, `staticFile`, `Audio` from `'remotion'`. Import library components from `'../components'` (in scene files) or `'./components'` (in ScriptVideo.tsx).

Build all files now."""


def _extract_json_array(text: str) -> str:
    """Extract a valid JSON array from text that may contain trailing garbage."""
    # Find the outermost matching brackets
    depth = 0
    start = text.index("[")
    for i, ch in enumerate(text[start:], start):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    # Fallback: strip common trailing junk
    text = text.strip()
    text = re.sub(r'```\s*$', '', text).strip()
    text = re.sub(r'[^}\]]+$', '', text).strip()
    return text


def parse_script_to_scenes(script: str, topic: str) -> list[dict]:
    """Use Claude to parse a generated script into structured scene data with visual segments."""
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=16384,
        system=PARSE_SYSTEM,
        messages=[
            {"role": "user", "content": PARSE_PROMPT.format(script=script)},
            {"role": "assistant", "content": "["},
        ],
    )
    raw = "[" + message.content[0].text
    raw = _extract_json_array(raw)
    try:
        scenes = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse scene JSON from Claude: {e}. Raw length: {len(raw)} chars") from e

    if not isinstance(scenes, list) or len(scenes) == 0:
        raise ValueError(f"Expected a non-empty list of scenes, got: {type(scenes).__name__}")

    return scenes


def generate_remotion_prompt(script: str, topic: str) -> dict:
    """Generate structured scene data and a Remotion composition prompt.

    Returns dict with:
      - scenes: scene data dict with scenes array and metadata
      - prompt: ready-to-use Remotion composition prompt string
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
