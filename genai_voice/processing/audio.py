"""audio.py — the voice layer: speech -> text (in) and text -> speech (out).

This is the part of the project that makes it an AUDIO bot. It is intentionally
separate from the agents: the agents only deal with text, and this module
converts between text and sound at the edges. Swapping the agents (the "brain")
never touches this file.

  * Speech -> text : OpenAI Whisper (the same model the original course used)
  * Text -> speech : gTTS (Google Text-to-Speech), saved as an .mp3
"""

from functools import lru_cache
from pathlib import Path

from gtts import gTTS

from genai_voice.config import defaults

# Where we write the spoken reply. It is in .gitignore so it never gets committed.
DEFAULT_SPEECH_FILE = defaults.PROJECT_ROOT / "temp_speech.mp3"


@lru_cache(maxsize=1)
def _openai_client():
    """Create the OpenAI client once (used only for Whisper transcription)."""
    from openai import OpenAI  # imported lazily so the app starts even without a key

    return OpenAI(api_key=defaults.OPENAI_API_KEY)


def speech_to_text(audio_path: str) -> str:
    """Transcribe a recorded audio file to text using Whisper.

    `audio_path` is the path to the file Gradio saved from the microphone.
    """
    if not audio_path:
        return ""
    with open(audio_path, "rb") as audio_file:
        transcript = _openai_client().audio.transcriptions.create(
            model=defaults.WHISPER_MODEL,
            file=audio_file,
        )
    return transcript.text.strip()


def text_to_speech(text: str, out_path: str | Path = DEFAULT_SPEECH_FILE) -> str:
    """Convert text to an .mp3 file and return its path (for playback in the UI)."""
    out_path = Path(out_path)
    gTTS(text=text, lang="en").save(str(out_path))
    return str(out_path)


class Audio:
    """Convenience wrapper kept for backwards compatibility (test_audio_simple.py).

    It bundles the two functions above and adds `communicate()`, which speaks a
    message out loud on your computer (handy for a quick local test).
    """

    def transcribe(self, audio_path: str) -> str:
        return speech_to_text(audio_path)

    def communicate(self, text: str) -> str:
        """Generate speech for `text` and try to play it on this machine."""
        path = text_to_speech(text)
        # Best-effort playback: on Windows this opens the default media player.
        # We ignore errors so a headless/server environment never crashes here.
        try:
            import os

            os.startfile(path)  # type: ignore[attr-defined]  # Windows only
        except Exception:
            pass
        return path
