"""
Voice Service - Multilingual Banking Assistant API
FastAPI service wrapping AI4Bharat models for voice, translation, and TTS
"""
import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import time

from config import settings, SUPPORTED_LANGUAGES
from asr import asr_model
from translate import translation_model
from tts import tts_model
from lid import lid_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Voice Service - Multilingual Banking Assistant",
    description="""
    AI-powered voice service for banking in Indian languages.

    Features:
    - **ASR**: Speech-to-text for 12+ Indian languages
    - **Translation**: English ↔ Indian language translation
    - **TTS**: Neural text-to-speech synthesis
    - **LID**: Automatic language identification

    All audio uses 16kHz mono WAV, base64-encoded.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ASRRequest(BaseModel):
    """Request model for ASR endpoint"""
    audio_b64: str = Field(..., description="Base64-encoded WAV audio (16kHz, mono)")
    language: str = Field(default="hi", description="Language code (hi, mr, ta, bn, etc.)")

    @validator('language')
    def validate_language(cls, v):
        valid_codes = [lang['code'] for lang in SUPPORTED_LANGUAGES]
        if v not in valid_codes:
            raise ValueError(f"Invalid language code. Must be one of: {valid_codes}")
        return v


class ASRResponse(BaseModel):
    """Response model for ASR endpoint"""
    transcript: str
    confidence: float
    language: str
    latency_ms: float
    model: str


class TranslationRequest(BaseModel):
    """Request model for Translation endpoint"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to translate")
    src: str = Field(..., description="Source language code")
    tgt: str = Field(..., description="Target language code")
    use_banking_glossary: bool = Field(
        default=True,
        description="Use banking glossary for better accuracy on domain terms"
    )

    @validator('src')
    def validate_src(cls, v):
        valid_codes = [lang['code'] for lang in SUPPORTED_LANGUAGES]
        if v not in valid_codes:
            raise ValueError(f"Invalid source language. Must be one of: {valid_codes}")
        return v

    @validator('tgt')
    def validate_tgt(cls, v):
        valid_codes = [lang['code'] for lang in SUPPORTED_LANGUAGES]
        if v not in valid_codes:
            raise ValueError(f"Invalid target language. Must be one of: {valid_codes}")
        return v


class TranslationResponse(BaseModel):
    """Response model for Translation endpoint"""
    translation: str
    source_language: str
    target_language: str
    direction: str
    latency_ms: float
    model: str


class TTSRequest(BaseModel):
    """Request model for TTS endpoint"""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to synthesize")
    language: str = Field(default="hi", description="Target language code")
    speaker: str = Field(default="female", description="Speaker preference (male/female)")

    @validator('language')
    def validate_language(cls, v):
        valid_codes = [lang['code'] for lang in SUPPORTED_LANGUAGES]
        if v not in valid_codes:
            raise ValueError(f"Invalid language code. Must be one of: {valid_codes}")
        return v


class TTSResponse(BaseModel):
    """Response model for TTS endpoint"""
    audio_b64: str
    duration_ms: int
    sample_rate: int
    language: str
    speaker: str
    latency_ms: float
    model: str


class LIDRequest(BaseModel):
    """Request model for LID endpoint"""
    audio_b64: str = Field(..., description="Base64-encoded WAV audio")


class LIDResponse(BaseModel):
    """Response model for LID endpoint"""
    language: str
    language_name: str
    confidence: float
    latency_ms: float
    method: str


class LanguageInfo(BaseModel):
    """Language information model"""
    code: str
    name: str
    script: str


# Startup event
@app.on_event("startup")
async def startup_event():
    """Log service startup information"""
    logger.info("=" * 60)
    logger.info("Voice Service Starting")
    logger.info("=" * 60)
    logger.info(f"Mock Mode: {settings.MOCK_MODE}")
    logger.info(f"Device: {settings.DEVICE}")
    logger.info(f"Model Path: {settings.MODEL_PATH}")
    logger.info(f"Supported Languages: {len(SUPPORTED_LANGUAGES)}")
    logger.info("=" * 60)


# Health endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Returns service status and model loading information
    """
    return {
        "status": "healthy",
        "service": "voice_service",
        "version": "1.0.0",
        "mock_mode": settings.MOCK_MODE,
        "device": settings.DEVICE,
        "models": {
            "asr": "loaded" if not settings.MOCK_MODE else "mock",
            "translate": "loaded" if not settings.MOCK_MODE else "mock",
            "tts": "loaded" if not settings.MOCK_MODE else "mock",
            "lid": "loaded" if not settings.MOCK_MODE else "mock",
        }
    }


# ASR endpoint
@app.post(
    "/asr",
    response_model=ASRResponse,
    tags=["Speech Recognition"],
    summary="Convert speech to text",
    description="Transcribe audio to text using IndicASR or Whisper"
)
async def speech_to_text(request: ASRRequest):
    """
    Automatic Speech Recognition endpoint

    Accepts base64-encoded WAV audio and returns transcript with confidence score.
    Supports 12+ Indian languages.
    """
    try:
        logger.info(f"ASR request for language: {request.language}")

        result = asr_model.transcribe(
            audio_b64=request.audio_b64,
            language=request.language
        )

        return ASRResponse(**result)

    except ValueError as e:
        logger.error(f"ASR validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"ASR processing error: {e}")
        raise HTTPException(status_code=500, detail="Speech recognition failed")


# Translation endpoint
@app.post(
    "/translate",
    response_model=TranslationResponse,
    tags=["Translation"],
    summary="Translate text between languages",
    description="Translate text using IndicTrans2 with banking domain awareness"
)
async def translate_text(request: TranslationRequest):
    """
    Translation endpoint

    Translates text between English and Indian languages.
    Supports banking domain glossary for accurate terminology translation.
    """
    try:
        logger.info(f"Translation request: {request.src} -> {request.tgtext}, src_lang={request.src}, tgt_lang={request.tgt}")

        result = translation_model.translate(
            text=request.text,
            src=request.src,
            tgt=request.tgt,
            use_banking_glossary=request.use_banking_glossary
        )

        return TranslationResponse(**result)

    except ValueError as e:
        logger.error(f"Translation validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Translation processing error: {e}")
        raise HTTPException(status_code=500, detail="Translation failed")


# TTS endpoint
@app.post(
    "/tts",
    response_model=TTSResponse,
    tags=["Text-to-Speech"],
    summary="Convert text to speech",
    description="Synthesize speech from text using IndicTTS neural synthesis"
)
async def text_to_speech(request: TTSRequest):
    """
    Text-to-Speech endpoint

    Synthesizes natural-sounding speech from text in multiple Indian languages.
    Returns base64-encoded audio data.
    """
    try:
        logger.info(f"TTS request for language: {request.language}, speaker: {request.speaker}")

        result = tts_model.synthesize(
            text=request.text,
            language=request.language,
            speaker=request.speaker
        )

        return TTSResponse(**result)

    except ValueError as e:
        logger.error(f"TTS validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"TTS processing error: {e}")
        raise HTTPException(status_code=500, detail="Speech synthesis failed")


# LID endpoint
@app.post(
    "/lid",
    response_model=LIDResponse,
    tags=["Language Identification"],
    summary="Identify language from audio",
    description="Automatically detect the language spoken in audio"
)
async def identify_language(request: LIDRequest):
    """
    Language Identification endpoint

    Analyzes audio and detects the language being spoken.
    Useful for automatic language routing.
    """
    try:
        logger.info("LID request received")

        result = lid_model.identify_audio(audio_b64=request.audio_b64)

        return LIDResponse(**result)

    except ValueError as e:
        logger.error(f"LID validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"LID processing error: {e}")
        raise HTTPException(status_code=500, detail="Language identification failed")


# Languages endpoint
@app.get(
    "/languages",
    response_model=List[LanguageInfo],
    tags=["Reference"],
    summary="Get supported languages",
    description="Returns list of all supported languages with their codes and scripts"
)
async def get_languages():
    """
    Get supported languages endpoint

    Returns a list of all supported languages with their codes,
    names, and writing scripts.
    """
    return SUPPORTED_LANGUAGES


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint

    Provides basic service information and links to documentation
    """
    return {
        "service": "Voice Service - Multilingual Banking Assistant",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "asr": "/asr",
            "translate": "/translate",
            "tts": "/tts",
            "lid": "/lid",
            "languages": "/languages"
        },
        "supported_languages": len(SUPPORTED_LANGUAGES)
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


# Run the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # Enable for development
        log_level="info"
    )
