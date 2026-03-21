"""WebSocket handler for real-time audio streaming."""

import json
import logging
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect

from session_store import session_store
from pipeline import Orchestrator
from models import (
    ClientMessage, ServerMessage,
    AudioChunkMessage, LanguageSelectMessage,
    StaffResponseMessage, SessionEndMessage,
    TranscriptMessage, TranslationMessage,
    SuggestionMessage, TTSAudioMessage,
    LIDResultMessage, ErrorMessage,
)

logger = logging.getLogger(__name__)


class WebSocketHandler:
    """Handles WebSocket connections and message routing."""

    def __init__(self):
        self.orchestrator = Orchestrator()

    async def handle_connection(
        self,
        websocket: WebSocket,
        session_id: str
    ):
        """Handle WebSocket connection for a session."""
        await websocket.accept()

        # Get or create session
        session = session_store.get_session(session_id)
        if not session:
            await self.send_error(
                websocket,
                f"Session {session_id} not found. "
                "Start a session with POST /session/start first"
            )
            await websocket.close()
            return

        logger.info(f"WebSocket connected for session {session_id}")

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)

                # Route message based on type
                await self.handle_message(websocket, session, message)

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for session {session_id}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from client: {e}")
            await self.send_error(websocket, f"Invalid JSON: {e}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}", exc_info=True)
            await self.send_error(websocket, f"Server error: {e}")
        finally:
            # Clean up orchestrator resources
            await self.orchestrator.close()

    async def handle_message(
        self,
        websocket: WebSocket,
        session,
        message: dict
    ):
        """Route incoming message to appropriate handler."""

        message_type = message.get("type")

        if message_type == "audio_chunk":
            await self.handle_audio_chunk(websocket, session, message)

        elif message_type == "language_select":
            await self.handle_language_select(websocket, session, message)

        elif message_type == "staff_response":
            await self.handle_staff_response(websocket, session, message)

        elif message_type == "session_end":
            await self.handle_session_end(websocket, session)

        else:
            await self.send_error(websocket, f"Unknown message type: {message_type}")

    async def handle_audio_chunk(
        self,
        websocket: WebSocket,
        session,
        message: dict
    ):
        """Handle audio chunk from customer."""
        try:
            audio_msg = AudioChunkMessage(**message)
            is_first_chunk = not session.lid_detected and not session.transcript

            logger.info(
                f"Processing audio chunk for session {session.session_id} "
                f"(first_chunk={is_first_chunk})"
            )

            # Process through pipeline
            results = await self.orchestrator.process_customer_audio(
                audio_b64=audio_msg.data,
                session=session,
                is_first_chunk=is_first_chunk
            )

            # Send results to client
            if "error" in results:
                await self.send_error(websocket, results["error"])
                return

            # Send LID result if available
            if results["lid"]:
                await self.send_message(websocket, LIDResultMessage(
                    language=results["lid"].language,
                    confidence=results["lid"].confidence
                ))

            # Send transcript
            if results["transcript"]:
                await self.send_message(websocket, TranscriptMessage(
                    text=results["transcript"].text,
                    language=results["transcript"].language,
                    confidence=results["transcript"].confidence
                ))

            # Send translation
            if results["translation"]:
                await self.send_message(websocket, TranslationMessage(
                    text=results["translation"].translated_text,
                    language=results["translation"].target_language
                ))

            # Send suggestions
            if results["suggestions"]:
                await self.send_message(websocket, SuggestionMessage(
                    suggestions=results["suggestions"].suggestions,
                    process_steps=results["suggestions"].process_steps,
                    escalate=results["suggestions"].escalate
                ))

        except Exception as e:
            logger.error(f"Error handling audio chunk: {e}", exc_info=True)
            await self.send_error(websocket, f"Error processing audio: {e}")

    async def handle_language_select(
        self,
        websocket: WebSocket,
        session,
        message: dict
    ):
        """Handle manual language selection."""
        try:
            lang_msg = LanguageSelectMessage(**message)
            session.language = lang_msg.language
            session.lid_detected = True  # Skip LID since language is set

            logger.info(
                f"Session {session.session_id} language set to: {lang_msg.language}"
            )

            # Confirm language selection to client
            await self.send_message(websocket, LIDResultMessage(
                language=lang_msg.language,
                confidence=1.0  # Manual selection = 100% confidence
            ))

        except Exception as e:
            logger.error(f"Error handling language select: {e}", exc_info=True)
            await self.send_error(websocket, f"Error setting language: {e}")

    async def handle_staff_response(
        self,
        websocket: WebSocket,
        session,
        message: dict
    ):
        """Handle staff text response."""
        try:
            staff_msg = StaffResponseMessage(**message)
            customer_language = session.language or "en"

            logger.info(
                f"Processing staff response for session {session.session_id}: "
                f"{staff_msg.text[:50]}..."
            )

            # Process through pipeline (translate + TTS)
            results = await self.orchestrator.process_staff_response(
                text=staff_msg.text,
                customer_language=customer_language
            )

            if "error" in results:
                await self.send_error(websocket, results["error"])
                return

            # Send TTS audio to client
            if results["tts"]:
                await self.send_message(websocket, TTSAudioMessage(
                    audio_b64=results["tts"].audio_data,
                    language=customer_language
                ))

            # Add to transcript
            session.add_transcript_entry(
                role="staff",
                text=staff_msg.text,
                language="en"
            )

        except Exception as e:
            logger.error(f"Error handling staff response: {e}", exc_info=True)
            await self.send_error(websocket, f"Error processing response: {e}")

    async def handle_session_end(
        self,
        websocket: WebSocket,
        session,
    ):
        """Handle session end signal."""
        logger.info(f"Session {session.session_id} ending")

        # Mark session as ended (don't delete yet, summary needed via REST)
        session.end_session()

        # Send confirmation
        await self.send_message(websocket, {
            "type": "session_ended",
            "session_id": session.session_id
        })

        # Close WebSocket
        await websocket.close()

    async def send_message(self, websocket: WebSocket, message: dict | ServerMessage):
        """Send a message to the WebSocket client."""
        if isinstance(message, dict):
            data = message
        else:
            data = message.model_dump()

        await websocket.send_json(data)

    async def send_error(self, websocket: WebSocket, message: str):
        """Send an error message to the WebSocket client."""
        await self.send_message(websocket, ErrorMessage(message=message))


# Global WebSocket handler instance
ws_handler = WebSocketHandler()
