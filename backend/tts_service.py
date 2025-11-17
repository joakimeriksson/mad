"""
Text-to-Speech service using Edge TTS for high-quality voice output.
"""

import edge_tts
import asyncio
from pathlib import Path
import tempfile
import os
from typing import Optional


class TTSService:
    """Service for converting text to speech using Microsoft Edge TTS."""

    # Available high-quality voices
    VOICES = {
        "en-US-female": "en-US-AriaNeural",      # Natural female voice
        "en-US-male": "en-US-GuyNeural",         # Natural male voice
        "en-GB-female": "en-GB-SoniaNeural",     # British female
        "en-GB-male": "en-GB-RyanNeural",        # British male
        "sv-SE-female": "sv-SE-SofieNeural",     # Swedish female
        "sv-SE-male": "sv-SE-MattiasNeural",     # Swedish male
    }

    def __init__(self, default_voice: str = "en-US-female"):
        """
        Initialize TTS service.

        Args:
            default_voice: Key from VOICES dict or direct voice name
        """
        self.default_voice = self.VOICES.get(default_voice, default_voice)
        self.audio_dir = Path(tempfile.gettempdir()) / "mad_tts"
        self.audio_dir.mkdir(exist_ok=True)

    async def generate_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        rate: str = "+0%",  # Speed: -50% to +100%
        pitch: str = "+0Hz",  # Pitch adjustment
    ) -> Path:
        """
        Generate speech from text and save to file.

        Args:
            text: Text to convert to speech
            voice: Voice to use (default: self.default_voice)
            rate: Speaking rate adjustment
            pitch: Pitch adjustment

        Returns:
            Path to generated audio file
        """
        if voice is None:
            voice = self.default_voice
        elif voice in self.VOICES:
            voice = self.VOICES[voice]

        # Generate unique filename
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        audio_file = self.audio_dir / f"tts_{text_hash}.mp3"

        # Check if already cached
        if audio_file.exists():
            return audio_file

        # Generate speech
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
        )

        await communicate.save(str(audio_file))

        return audio_file

    def cleanup_old_files(self, max_age_hours: int = 24):
        """Remove audio files older than max_age_hours."""
        import time
        now = time.time()
        max_age_seconds = max_age_hours * 3600

        for audio_file in self.audio_dir.glob("tts_*.mp3"):
            if now - audio_file.stat().st_mtime > max_age_seconds:
                audio_file.unlink()

    @classmethod
    async def list_available_voices(cls) -> list:
        """List all available Edge TTS voices."""
        voices = await edge_tts.list_voices()
        return voices
