"""Pydantic models for WebSocket and REST API messages."""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
import uuid


# ============================================================================
# WebSocket Client Messages (Browser → Gateway)
# ============================================================================

class AudioChunkMessage(BaseModel):
    """Client sends audio data chunk."""
    type: Literal["audio_chunk"] = "audio_chunk"
    data: str = Field(..., description="Base64 encoded audio data")


class LanguageSelectMessage(BaseModel):
    """Client selects/detects a language."""
    type: Literal["language_select"] = "language_select"
    language: str = Field(..., description="Language code (e.g., 'hi', 'en', 'es')")


class StaffResponseMessage(BaseModel):
    """Staff sends a text response to be spoken to customer."""
    type: Literal["staff_response"] = "staff_response"
    text: str = Field(..., description="Text response from staff")
    language: str = Field(..., description="Target language for TTS")


class SessionEndMessage(BaseModel):
    """Client signals session end."""
    type: Literal["session_end"] = "session_end"


# Union type for all client messages
ClientMessage = AudioChunkMessage | LanguageSelectMessage | StaffResponseMessage | SessionEndMessage


# ============================================================================
# WebSocket Server Messages (Gateway → Browser)
# ============================================================================

class TranscriptMessage(BaseModel):
    """Server sends ASR transcript."""
    type: Literal["transcript"] = "transcript"
    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected/specified language")
    confidence: float = Field(..., ge=0.0, le=1.0, description="ASR confidence score")


class TranslationMessage(BaseModel):
    """Server sends translation result."""
    type: Literal["translation"] = "translation"
    text: str = Field(..., description="Translated text")
    language: str = Field(..., description="Target language code")


class SuggestionMessage(BaseModel):
    """Server sends AI suggestions from LLM service."""
    type: Literal["suggestion"] = "suggestion"
    suggestions: List[str] = Field(default_factory=list, description="Suggested responses")
    process_steps: List[str] = Field(default_factory=list, description="Processing steps taken")
    escalate: bool = Field(default=False, description="Whether to escalate to human")


class TTSAudioMessage(BaseModel):
    """Server sends TTS audio."""
    type: Literal["tts_audio"] = "tts_audio"
    audio_b64: str = Field(..., description="Base64 encoded audio data")
    language: str = Field(..., description="Language of the TTS")


class LIDResultMessage(BaseModel):
    """Server sends language detection result."""
    type: Literal["lid_result"] = "lid_result"
    language: str = Field(..., description="Detected language code")
    confidence: float = Field(..., ge=0.0, le=1.0, description="LID confidence score")


class ErrorMessage(BaseModel):
    """Server sends error message."""
    type: Literal["error"] = "error"
    message: str = Field(..., description="Error description")


# Union type for all server messages
ServerMessage = TranscriptMessage | TranslationMessage | SuggestionMessage | TTSAudioMessage | LIDResultMessage | ErrorMessage


# ============================================================================
# REST API Models
# ============================================================================

class SessionStartResponse(BaseModel):
    """Response for POST /session/start"""
    session_id: str = Field(..., description="Unique session identifier")


class SessionEndResponse(BaseModel):
    """Response for POST /session/{id}/end"""
    summary_en: str = Field(..., description="Session summary in English")
    summary_lang: str = Field(..., description="Session summary in customer language")
    query_type: str = Field(..., description="Classification of query type")


class TranscriptEntry(BaseModel):
    """Single transcript entry."""
    role: Literal["customer", "staff"] = Field(..., description="Who spoke")
    text: str = Field(..., description="What was said")
    language: str = Field(..., description="Language code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When it was said")


class TranscriptResponse(BaseModel):
    """Response for GET /session/{id}/transcript"""
    transcript: List[TranscriptEntry] = Field(default_factory=list, description="Full conversation history")


# ============================================================================
# Internal Service Models
# ============================================================================

class ASRRequest(BaseModel):
    """Request to voice_service /asr"""
    audio_data: str = Field(..., description="Base64 encoded audio")
    language: Optional[str] = Field(None, description="Language code (None for auto-detect)")


class ASRResponse(BaseModel):
    """Response from voice_service /asr"""
    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected language")
    confidence: float = Field(..., description="Confidence score")


class LIDRequest(BaseModel):
    """Request to voice_service /lid"""
    audio_data: str = Field(..., description="Base64 encoded audio")


class LIDResponse(BaseModel):
    """Response from voice_service /lid"""
    language: str = Field(..., description="Detected language code")
    confidence: float = Field(..., description="Confidence score")


class TranslateRequest(BaseModel):
    """Request to voice_service /translate"""
    text: str = Field(..., description="Text to translate")
    source_language: str = Field(..., alias="source_language", description="Source language code")
    target_language: str = Field(..., alias="target_language", description="Target language code")


class TranslateResponse(BaseModel):
    """Response from voice_service /translate"""
    translated_text: str = Field(..., description="Translated text")
    source_language: str = Field(..., description="Source language code")
    target_language: str = Field(..., description="Target language code")


class TTSRequest(BaseModel):
    """Request to voice_service /tts"""
    text: str = Field(..., description="Text to synthesize")
    language: str = Field(..., description="Language code")


class TTSResponse(BaseModel):
    """Response from voice_service /tts"""
    audio_data: str = Field(..., description="Base64 encoded audio")
    language: str = Field(..., description="Language code")


class SuggestRequest(BaseModel):
    """Request to llm_service /suggest"""
    query: str = Field(..., description="Customer query (translated to English)")
    conversation_history: List[dict] = Field(default_factory=list, description="Previous messages")
    customer_language: str = Field(..., description="Customer's language code")


class SuggestResponse(BaseModel):
    """Response from llm_service /suggest"""
    suggestions: List[str] = Field(default_factory=list, description="Suggested responses")
    process_steps: List[str] = Field(default_factory=list, description="Processing steps")
    escalate: bool = Field(default=False, description="Whether to escalate")


class SummarizeRequest(BaseModel):
    """Request to llm_service /summarize"""
    conversation: List[dict] = Field(..., description="Full conversation history")
    customer_language: str = Field(..., description="Customer's language code")


class SummarizeResponse(BaseModel):
    """Response from llm_service /summarize"""
    summary_en: str = Field(..., description="Summary in English")
    summary_lang: str = Field(..., description="Summary in customer language")
    query_type: str = Field(..., description="Query classification")
