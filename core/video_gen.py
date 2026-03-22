"""Generate Remotion video components by sending the prompt to Claude API with tool_use."""

import os
import re
import subprocess

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REMOTION_SRC = os.path.join(_app_dir, "remotion", "src")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

WRITE_FILE_TOOL = {
    "name": "write_file",
    "description": (
        "Write content to a file in the Remotion project at remotion/src/. "
        "Used to create React/TSX components, update Root.tsx, etc."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": (
                    "Relative path within remotion/src/ "
                    "(e.g. 'ScriptVideo.tsx', 'scenes/HookScene.tsx', 'components/AnimatedText.tsx')"
                ),
            },
            "content": {
                "type": "string",
                "description": "The full file content to write",
            },
        },
        "required": ["path", "content"],
    },
}

SYSTEM_PROMPT = (
    "You are a Remotion/React expert. Use the write_file tool to create each component file. "
    "Write all files needed to build the video composition. Do not explain — just write the files. "
    "IMPORTANT: The components/ directory contains pre-built library components. "
    "Do NOT overwrite files in components/ — import and use them as-is."
)

# Protected paths: library components that should not be overwritten
PROTECTED_PREFIXES = ("components/",)

VALID_EXTENSIONS = {".tsx", ".ts", ".css", ".json"}


def _sanitize_path(path: str) -> str | None:
    """Validate and sanitize a relative path under remotion/src/. Returns None if invalid."""
    path = path.strip().lstrip("/").lstrip("\\")
    # Reject path traversal
    if ".." in path:
        return None
    # Check extension
    _, ext = os.path.splitext(path)
    if ext.lower() not in VALID_EXTENSIONS:
        return None
    # Resolve and confirm it stays under REMOTION_SRC
    full = os.path.normpath(os.path.join(REMOTION_SRC, path))
    if not full.startswith(os.path.normpath(REMOTION_SRC)):
        return None
    return full


def generate_video_components(prompt: str, progress_callback=None) -> list[str]:
    """Send the Remotion prompt to Claude with tool_use and write generated files.

    Args:
        prompt: The full Remotion prompt string from generate_remotion_prompt().
        progress_callback: Optional callable(message: str) for progress updates.

    Returns:
        List of file paths (relative to remotion/src/) that were written.
    """
    files_written = []
    messages = [{"role": "user", "content": prompt}]

    def _progress(msg: str):
        if progress_callback:
            progress_callback(msg)

    _progress("Sending prompt to Claude...")

    while True:
        # Use streaming to avoid Anthropic's 10-minute timeout on long requests
        with client.messages.stream(
            model=CLAUDE_MODEL,
            max_tokens=32000,
            system=SYSTEM_PROMPT,
            tools=[WRITE_FILE_TOOL],
            messages=messages,
        ) as stream:
            response = stream.get_final_message()

        # Process response content blocks
        assistant_content = response.content
        tool_results = []

        for block in assistant_content:
            if block.type == "tool_use" and block.name == "write_file":
                rel_path = block.input.get("path", "")
                content = block.input.get("content", "")

                full_path = _sanitize_path(rel_path)
                if full_path is None:
                    _progress(f"Skipped invalid path: {rel_path}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Error: invalid path '{rel_path}'",
                    })
                    continue

                # Protect library components from being overwritten
                if any(rel_path.startswith(p) for p in PROTECTED_PREFIXES) and os.path.exists(full_path):
                    _progress(f"Skipped protected: {rel_path}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"PROTECTED: '{rel_path}' is a library component. Import and use it, do not rewrite.",
                    })
                    continue

                # Create parent dirs and write file
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

                files_written.append(rel_path)
                _progress(f"Wrote {rel_path}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": "OK",
                })

        # If no tool calls, Claude is done
        if not tool_results:
            break

        # Continue the agentic loop
        messages.append({"role": "assistant", "content": assistant_content})
        messages.append({"role": "user", "content": tool_results})

        # Also break if Claude signals end_turn with tool results
        # (shouldn't happen, but safety check)
        if response.stop_reason == "end_turn":
            break

    _progress(f"Done — wrote {len(files_written)} files")

    # Auto-sync: commit and push generated files to git
    _sync_to_git(files_written, _progress)

    return files_written


def _sync_to_git(files: list[str], progress_callback=None):
    """Commit and push generated Remotion files so they can be pulled locally."""
    if not files:
        return

    def _progress(msg: str):
        if progress_callback:
            progress_callback(msg)

    try:
        # Stage all generated files (components + scene data + images)
        git_paths = [os.path.join("remotion", "src", f) for f in files]
        # Also stage scene data and generated images
        git_paths.append(os.path.join("remotion", "src", "data", "script.json"))
        images_dir = os.path.join("remotion", "public", "images")
        if os.path.isdir(os.path.join(_app_dir, images_dir)):
            git_paths.append(images_dir)
        subprocess.run(
            ["git", "add"] + git_paths,
            cwd=_app_dir, check=True, capture_output=True, text=True,
        )

        # Commit
        subprocess.run(
            ["git", "commit", "-m", "Auto-generated Remotion video components"],
            cwd=_app_dir, check=True, capture_output=True, text=True,
        )

        # Push
        subprocess.run(
            ["git", "push"],
            cwd=_app_dir, check=True, capture_output=True, text=True,
        )
        _progress("Synced to git — run `git pull` locally")
    except subprocess.CalledProcessError as e:
        _progress(f"Git sync failed: {e.stderr.strip() or e.stdout.strip()}")
