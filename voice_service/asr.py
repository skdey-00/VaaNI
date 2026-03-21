"""
Automatic Speech Recognition (ASR) Module
Uses IndicWav2Vec for Indian languages and Whisper as fallback
"""
import time
import base64
import logging
from typing import Dict, Optional
import torch
from transformers import (
    AutoModelForCTC,
    AutoProcessor,
    WhisperForConditionalGeneration,
    WhisperProcessor,
)
import numpy as np
import io
from scipy.io import wavfile

from config import settings
from banking_glossary import get_glossary_terms

logger = logging.getLogger(__name__)


class ASRModel:
    """ASR Model Handler for Indic Languages"""

    def __init__(self):
        self.model = None
        self.processor = None
        self.device = settings.DEVICE
        self.model_type = None

        if not settings.MOCK_MODE:
            self._load_model()

    def _load_model(self):
        """Load the ASR model"""
        try:
            logger.info(f"Loading ASR model on {self.device}...")
            start_time = time.time()

            # Try IndicWav2Vec first for Indian languages
            model_name = "AI4Bharat/indicwav2vec_vakyansh_hindi"

            try:
                self.processor = AutoProcessor.from_pretrained(model_name)
                self.model = AutoModelForCTC.from_pretrained(model_name)

                if self.device == "cuda" and torch.cuda.is_available():
                    self.model = self.model.to(self.device)

                self.model_type = "indicwav2vec"
                logger.info(f"Loaded IndicWav2Vec model in {time.time() - start_time:.2f}s")

            except Exception as e:
                logger.warning(f"IndicWav2Vec loading failed: {e}, falling back to Whisper")
                self._load_whisper()

        except Exception as e:
            logger.error(f"Failed to load ASR model: {e}")
            self.model = None

    def _load_whisper(self):
        """Load Whisper as fallback"""
        try:
            model_name = "openai/whisper-small"
            self.processor = WhisperProcessor.from_pretrained(model_name)
            self.model = WhisperForConditionalGeneration.from_pretrained(model_name)

            if self.device == "cuda" and torch.cuda.is_available():
                self.model = self.model.to(self.device)

            self.model_type = "whisper"
            logger.info("Loaded Whisper model as fallback")

        except Exception as e:
            logger.error(f"Failed to load Whisper: {e}")

    def _decode_audio(self, audio_b64: str) -> tuple:
        """Decode base64 audio to numpy array"""
        try:
            audio_bytes = base64.b64decode(audio_b64)
            audio_io = io.BytesIO(audio_bytes)

            # Read WAV file
            sample_rate, audio_data = wavfile.read(audio_io)

            # Convert to float if needed
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            elif audio_data.dtype == np.int32:
                audio_data = audio_data.astype(np.float32) / 2147483648.0

            return sample_rate, audio_data

        except Exception as e:
            logger.error(f"Audio decoding error: {e}")
            raise ValueError(f"Invalid audio data: {e}")

    def transcribe(
        self, audio_b64: str, language: str = "hi"
    ) -> Dict[str, any]:
        """
        Transcribe audio to text

        Args:
            audio_b64: Base64 encoded audio data
            language: Language code (hi, mr, ta, bn, etc.)

        Returns:
            Dictionary with transcript and confidence
        """
        start_time = time.time()

        if settings.MOCK_MODE:
            return self._mock_transcribe(language)

        if self.model is None:
            raise RuntimeError("ASR model not loaded")

        try:
            # Decode audio
            sample_rate, audio_data = self._decode_audio(audio_b64)

            # Resample if needed (models expect 16kHz)
            if sample_rate != 16000:
                from scipy import signal
                number_of_samples = round(len(audio_data) * float(16000) / sample_rate)
                audio_data = signal.resample(audio_data, number_of_samples)

            # Prepare inputs
            if self.model_type == "indicwav2vec":
                inputs = self.processor(
                    audio_data,
                    sampling_rate=16000,
                    return_tensors="pt"
                )

                if self.device == "cuda":
                    inputs = inputs.to(self.device)

                # Generate
                with torch.no_grad():
                    logits = self.model(inputs.input_values).logits
                    predicted_ids = torch.argmax(logits, dim=-1)
                    transcript = self.processor.decode(predicted_ids[0])

            else:  # whisper
                inputs = self.processor(
                    audio_data,
                    sampling_rate=16000,
                    return_tensors="pt"
                )

                if self.device == "cuda":
                    inputs = inputs.to(self.device)

                # Generate with forced language
                forced_decoder_ids = self.processor.get_decoder_prompt_ids(
                    language=language,
                    task="transcribe"
                )

                with torch.no_grad():
                    predicted_ids = self.model.generate(
                        inputs.input_features,
                        forced_decoder_ids=forced_decoder_ids
                    )
                    transcript = self.processor.decode(predicted_ids[0], skip_special_tokens=True)

            # Calculate pseudo-confidence (simplified)
            confidence = 0.95  # Placeholder

            latency_ms = (time.time() - start_time) * 1000

            logger.info(f"ASR completed in {latency_ms:.0f}ms (target: <{settings.ASR_MAX_LATENCY_MS}ms)")

            return {
                "transcript": transcript.strip(),
                "confidence": confidence,
                "language": language,
                "latency_ms": round(latency_ms, 2),
                "model": self.model_type
            }

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            raise

    def _mock_transcribe(self, language: str) -> Dict[str, any]:
        """Generate mock transcription for development"""
        mock_responses = {
            "hi": "मेरे बैंक अकाउंट का बैलेंस बताएं",
            "mr": "माझे बँक खाते शिल्लक किती आहे",
            "ta": "என் வங்கி கணக்கு இருப்பை சொல்லுங்கள்",
            "bn": "আমার ব্যাংক অ্যাকাউন্টের ব্যালান্স বলুন",
            "en": "Tell me my bank account balance",
        }

        transcript = mock_responses.get(language, mock_responses["en"])

        return {
            "transcript": transcript,
            "confidence": 0.98,
            "language": language,
            "latency_ms": 15.0,
            "model": "mock"
        }


# Global model instance
asr_model = ASRModel()
