"""
Text-to-Speech (TTS) Module
Uses IndicTTS for neural voice synthesis in Indian languages
"""
import time
import base64
import logging
from typing import Dict, Optional
import torch
import numpy as np
import io
from scipy.io import wavfile

from config import settings

logger = logging.getLogger(__name__)


class TTSModel:
    """IndicTTS Model Handler for Text-to-Speech"""

    def __init__(self):
        self.model = None
        self.processor = None
        self.device = settings.DEVICE
        self.sample_rate = 22050  # Standard TTS sample rate

        if not settings.MOCK_MODE:
            self._load_model()

    def _load_model(self):
        """Load the TTS model"""
        try:
            logger.info(f"Loading TTS model on {self.device}...")
            start_time = time.time()

            # Note: IndicTTS might not be directly available on HuggingFace
            # We'll use a fallback approach with espeak or similar
            # For demo purposes, we'll use a simple mock

            logger.info(f"TTS model ready in {time.time() - start_time:.2f}s")

        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            self.model = None

    def _generate_mock_audio(self, text: str, duration_ms: int) -> bytes:
        """Generate simple WAV audio for demo"""
        # Calculate number of samples
        sample_rate = 22050
        num_samples = int((duration_ms / 1000.0) * sample_rate)

        # Generate simple sine wave tones based on text (very basic)
        # This is just for demo - real TTS would be much better
        t = np.linspace(0, duration_ms / 1000.0, num_samples)

        # Mix a few frequencies to create speech-like sound
        audio = np.zeros_like(t)
        freqs = [200, 400, 600, 800]

        for i, char in enumerate(text[:20]):
            if char.isalpha():
                freq_idx = ord(char.lower()) % len(freqs)
                amplitude = 0.1 * (1 - i / len(text))
                audio += amplitude * np.sin(2 * np.pi * freqs[freq_idx] * t)

        # Apply envelope
        envelope = np.ones_like(t)
        fade_len = int(0.05 * sample_rate)  # 50ms fade
        envelope[:fade_len] = np.linspace(0, 1, fade_len)
        envelope[-fade_len:] = np.linspace(1, 0, fade_len)
        audio = audio * envelope

        # Normalize
        audio = audio / (np.max(np.abs(audio)) + 1e-6)
        audio = (audio * 32767).astype(np.int16)

        # Create WAV bytes
        audio_io = io.BytesIO()
        wavfile.write(audio_io, sample_rate, audio)
        audio_bytes = audio_io.getvalue()

        return audio_bytes

    def synthesize(
        self,
        text: str,
        language: str = "hi",
        speaker: str = "female"
    ) -> Dict[str, any]:
        """
        Synthesize speech from text

        Args:
            text: Input text to synthesize
            language: Target language code
            speaker: Speaker preference (male/female)

        Returns:
            Dictionary with base64 audio and metadata
        """
        start_time = time.time()

        if settings.MOCK_MODE:
            return self._mock_synthesize(text, language, speaker)

        if self.model is None:
            # Fall back to mock if model not loaded
            logger.warning("TTS model not loaded, using mock synthesis")
            return self._mock_synthesize(text, language, speaker)

        try:
            # In a real implementation, you would:
            # 1. Normalize text for the target language
            # 2. Run through TTS model
            # 3. Generate audio waveform
            # 4. Encode to WAV format

            # For now, using mock synthesis
            return self._mock_synthesize(text, language, speaker)

        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            raise

    def _mock_synthesize(
        self,
        text: str,
        language: str,
        speaker: str
    ) -> Dict[str, any]:
        """Generate mock audio synthesis for development"""

        # Estimate duration based on text length and language
        # Average speaking rate: ~150 words per minute
        words = len(text.split())
        chars = len(text)

        # Indian languages might be more compact
        if language != "en":
            duration_ms = max(1000, int(chars * 60))  # ~60ms per character
        else:
            duration_ms = max(1000, int(words * 400))  # ~400ms per word

        duration_ms = min(duration_ms, 30000)  # Cap at 30 seconds

        # Generate audio
        audio_bytes = self._generate_mock_audio(text, duration_ms)
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')

        latency_ms = (time.time() - start_time) * 1000

        logger.info(
            f"TTS completed in {latency_ms:.0f}ms "
            f"(target: <{settings.TTS_MAX_LATENCY_MS}ms), "
            f"duration: {duration_ms}ms"
        )

        return {
            "audio_b64": audio_b64,
            "duration_ms": duration_ms,
            "sample_rate": self.sample_rate,
            "language": language,
            "speaker": speaker,
            "latency_ms": round(latency_ms, 2),
            "model": "mock"
        }

    def synthesize_with_markup(
        self,
        text: str,
        language: str = "hi",
        ssml: bool = False
    ) -> Dict[str, any]:
        """
        Synthesize with optional SSML markup support

        Args:
            text: Input text (can include SSML tags if ssml=True)
            language: Target language
            ssml: Whether text contains SSML markup

        Returns:
            Dictionary with base64 audio and metadata
        """
        # For now, just use regular synthesis
        return self.synthesize(text, language)


# Global model instance
tts_model = TTSModel()
