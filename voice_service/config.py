"""
Configuration for Voice Service - Multilingual Banking Assistant
"""
import os
from typing import List, Dict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Model Configuration
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models")
    DEVICE: str = os.getenv("DEVICE", "cpu")  # 'cpu' or 'cuda'
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "false").lower() == "true"

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "1"))

    # Model Names (HuggingFace)
    ASR_MODEL: str = "AI4Bharat/indicwav2vec_vakyansh_bengali"
    TRANSLATE_MODEL: str = "AI4Bharat/indictrans2-en-indic-1B"
    TTS_MODEL: str = "AI4Bharat/indicTTS"
    LID_MODEL: str = "AI4Bharat/IndicLID"

    # Audio Configuration
    SAMPLE_RATE: int = 16000
    AUDIO_CHANNELS: int = 1
    AUDIO_FORMAT: str = "wav"

    # Performance
    MAX_AUDIO_LENGTH_SECONDS: int = 30
    MAX_TEXT_LENGTH: int = 5000
    ASR_MAX_LATENCY_MS: int = 500
    TRANSLATE_MAX_LATENCY_MS: int = 400
    TTS_MAX_LATENCY_MS: int = 600

    class Config:
        env_file = ".env"
        case_sensitive = True


# Supported Indian Languages with banking terminology coverage
SUPPORTED_LANGUAGES: List[Dict[str, str]] = [
    {"code": "en", "name": "English", "script": "Latin"},
    {"code": "hi", "name": "Hindi", "script": "Devanagari"},
    {"code": "mr", "name": "Marathi", "script": "Devanagari"},
    {"code": "ta", "name": "Tamil", "script": "Tamil"},
    {"code": "bn", "name": "Bengali", "script": "Bengali"},
    {"code": "te", "name": "Telugu", "script": "Telugu"},
    {"code": "kn", "name": "Kannada", "script": "Kannada"},
    {"code": "ml", "name": "Malayalam", "script": "Malayalam"},
    {"code": "gu", "name": "Gujarati", "script": "Gujarati"},
    {"code": "or", "name": "Odia", "script": "Odia"},
    {"code": "pa", "name": "Punjabi", "script": "Gurmukhi"},
    {"code": "as", "name": "Assamese", "script": "Assamese"},
]

# Language name to code mapping
LANG_CODE_MAP = {lang["name"].lower(): lang["code"] for lang in SUPPORTED_LANGUAGES}
LANG_CODE_MAP.update({lang["code"]: lang["code"] for lang in SUPPORTED_LANGUAGES})

# Initialize settings
settings = Settings()
