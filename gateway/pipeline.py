"""Pipeline orchestration for voice_service and llm_service calls."""

import asyncio
import logging
from typing import Optional, Tuple
import httpx

from config import (
    VOICE_SERVICE_URL,
    LLM_SERVICE_URL,
    ENABLE_LID,
    AUTO_TRANSLATE,
    AUTO_SUGGEST,
    MAX_RETRIES,
    RETRY_DELAY_MS,
)
from models import (
    ASRRequest, ASRResponse,
    LIDRequest, LIDResponse,
    TranslateRequest, TranslateResponse,
    TTSRequest, TTSResponse,
    SuggestRequest, SuggestResponse,
)

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Custom exception for pipeline errors."""
    pass


class VoiceServicePipeline:
    """Orchestrates calls to voice_service."""

    def __init__(self):
        self.voice_client = httpx.AsyncClient(
            base_url=VOICE_SERVICE_URL,
            timeout=httpx.Timeout(30.0)
        )

    async def close(self):
        """Close the HTTP client."""
        await self.voice_client.aclose()

    async def _retry_request(self, request_fn, *args, **kwargs):
        """Retry a request with exponential backoff."""
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                return await request_fn(*args, **kwargs)
            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY_MS * (2 ** attempt) / 1000
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}), "
                        f"retrying in {delay}s: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Request failed after {MAX_RETRIES} attempts: {e}")

        raise PipelineError(f"Service request failed: {last_error}")

    async def detect_language(self, audio_b64: str) -> LIDResponse:
        """Call voice_service /lid to detect language."""
        if not ENABLE_LID:
            logger.info("LID disabled, skipping language detection")
            return None

        logger.info("Calling voice_service /lid")

        async def _request():
            response = await self.voice_client.post(
                "/lid",
                json=LIDRequest(audio_data=audio_b64).model_dump()
            )
            response.raise_for_status()
            return LIDResponse(**response.json())

        return await self._retry_request(_request)

    async def transcribe(
        self,
        audio_b64: str,
        language: Optional[str] = None
    ) -> ASRResponse:
        """Call voice_service /asr to transcribe audio."""
        logger.info(f"Calling voice_service /asr with language={language}")

        async def _request():
            response = await self.voice_client.post(
                "/asr",
                json=ASRRequest(
                    audio_data=audio_b64,
                    language=language
                ).model_dump(by_alias=True)
            )
            response.raise_for_status()
            return ASRResponse(**response.json())

        return await self._retry_request(_request)

    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> TranslateResponse:
        """Call voice_service /translate to translate text."""
        logger.info(
            f"Calling voice_service /translate: "
            f"{source_language} -> {target_language}"
        )

        async def _request():
            response = await self.voice_client.post(
                "/translate",
                json=TranslateRequest(
                    text=text,
                    source_language=source_language,
                    target_language=target_language
                ).model_dump(by_alias=True)
            )
            response.raise_for_status()
            return TranslateResponse(**response.json())

        return await self._retry_request(_request)

    async def text_to_speech(
        self,
        text: str,
        language: str
    ) -> TTSResponse:
        """Call voice_service /tts to synthesize speech."""
        logger.info(f"Calling voice_service /tts for language={language}")

        async def _request():
            response = await self.voice_client.post(
                "/tts",
                json=TTSRequest(text=text, language=language).model_dump()
            )
            response.raise_for_status()
            return TTSResponse(**response.json())

        return await self._retry_request(_request)


class LLMServicePipeline:
    """Orchestrates calls to llm_service."""

    def __init__(self):
        self.llm_client = httpx.AsyncClient(
            base_url=LLM_SERVICE_URL,
            timeout=httpx.Timeout(30.0)
        )

    async def close(self):
        """Close the HTTP client."""
        await self.llm_client.aclose()

    async def get_suggestions(
        self,
        query: str,
        conversation_history: list,
        customer_language: str
    ) -> SuggestResponse:
        """Call llm_service /suggest to get AI suggestions."""
        logger.info("Calling llm_service /suggest")

        async def _request():
            response = await self.llm_client.post(
                "/suggest",
                json=SuggestRequest(
                    query=query,
                    conversation_history=conversation_history,
                    customer_language=customer_language
                ).model_dump()
            )
            response.raise_for_status()
            return SuggestResponse(**response.json())

        try:
            return await self._request()
        except (httpx.HTTPError, asyncio.TimeoutError) as e:
            logger.error(f"LLM service request failed: {e}")
            # Return empty suggestions on failure
            return SuggestResponse(
                suggestions=[],
                process_steps=["LLM service unavailable"],
                escalate=True  # Escalate if LLM fails
            )

    async def summarize_conversation(
        self,
        conversation: list,
        customer_language: str
    ) -> Tuple[str, str, str]:
        """
        Call llm_service /summarize to get session summary.
        Returns (summary_en, summary_lang, query_type)
        """
        logger.info("Calling llm_service /summarize")

        async def _request():
            response = await self.llm_client.post(
                "/summarize",
                json={
                    "conversation": conversation,
                    "customer_language": customer_language
                }
            )
            response.raise_for_status()
            data = response.json()
            return (
                data.get("summary_en", ""),
                data.get("summary_lang", ""),
                data.get("query_type", "general")
            )

        try:
            return await self._request()
        except (httpx.HTTPError, asyncio.TimeoutError) as e:
            logger.error(f"LLM summarize request failed: {e}")
            # Return basic summary on failure
            transcript_text = "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('text', '')}"
                for msg in conversation
            ])
            return (
                f"Conversation summary unavailable due to error: {str(e)}",
                transcript_text,
                "unclassified"
            )


class Orchestrator:
    """Main orchestrator that combines voice and LLM services."""

    def __init__(self):
        self.voice = VoiceServicePipeline()
        self.llm = LLMServicePipeline()

    async def close(self):
        """Close all HTTP clients."""
        await self.voice.close()
        await self.llm.close()

    async def process_customer_audio(
        self,
        audio_b64: str,
        session,
        is_first_chunk: bool = False
    ) -> dict:
        """
        Process customer audio through the full pipeline.
        Returns dict with results for each step.
        """
        results = {
            "lid": None,
            "transcript": None,
            "translation": None,
            "suggestions": None,
        }

        try:
            # Step 1: Language Detection (if first chunk and no language set)
            if is_first_chunk and ENABLE_LID and not session.language:
                lid_result = await self.voice.detect_language(audio_b64)
                if lid_result:
                    session.language = lid_result.language
                    session.lid_detected = True
                    results["lid"] = lid_result
                    logger.info(
                        f"LID detected language: {lid_result.language} "
                        f"(confidence: {lid_result.confidence:.2f})"
                    )

            # Use detected/selected language, or default
            language = session.language or "en"

            # Step 2: Transcribe audio
            transcript_result = await self.voice.transcribe(
                audio_b64,
                language=language
            )
            results["transcript"] = transcript_result

            # Add to transcript
            session.add_transcript_entry(
                role="customer",
                text=transcript_result.text,
                language=transcript_result.language
            )

            # Step 3: Translate to English (if not already English)
            if AUTO_TRANSLATE and transcript_result.language != "en":
                translation_result = await self.voice.translate(
                    text=transcript_result.text,
                    source_language=transcript_result.language,
                    target_language="en"
                )
                results["translation"] = translation_result
                query_text = translation_result.translated_text
            else:
                query_text = transcript_result.text

            # Step 4: Get suggestions from LLM
            if AUTO_SUGGEST:
                history = session.get_history_for_llm()
                suggestions_result = await self.llm.get_suggestions(
                    query=query_text,
                    conversation_history=history,
                    customer_language=session.language or "en"
                )
                results["suggestions"] = suggestions_result

        except PipelineError as e:
            logger.error(f"Pipeline error processing customer audio: {e}")
            results["error"] = str(e)

        return results

    async def process_staff_response(
        self,
        text: str,
        customer_language: str
    ) -> dict:
        """
        Process staff response through translation and TTS pipeline.
        Returns dict with translation and TTS audio.
        """
        results = {
            "translation": None,
            "tts": None,
        }

        try:
            # Step 1: Translate from English to customer language
            if customer_language != "en":
                translation_result = await self.voice.translate(
                    text=text,
                    source_language="en",
                    target_language=customer_language
                )
                results["translation"] = translation_result
                text_to_speak = translation_result.translated_text
            else:
                text_to_speak = text

            # Step 2: Generate TTS audio
            tts_result = await self.voice.text_to_speech(
                text=text_to_speak,
                language=customer_language
            )
            results["tts"] = tts_result

        except PipelineError as e:
            logger.error(f"Pipeline error processing staff response: {e}")
            results["error"] = str(e)

        return results
