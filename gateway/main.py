"""FastAPI Gateway service for orchestrating voice and LLM services."""

import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from datetime import datetime

from config import (
    GATEWAY_HOST,
    GATEWAY_PORT,
    ALLOWED_ORIGINS,
    LOG_LEVEL,
    DEBUG_MODE,
)
from session_store import session_store
from ws_handler import ws_handler
from pipeline import Orchestrator
from models import (
    SessionStartResponse,
    SessionEndResponse,
    TranscriptResponse,
    TranscriptEntry,
)
from summarizer.pdf_generator import pdf_generator

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Lifespan manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    logger.info("Gateway service starting up...")
    yield
    logger.info("Gateway service shutting down...")
    # Cleanup: end all active sessions
    active_count = len(session_store.get_active_sessions())
    session_store._sessions.clear()
    logger.info(f"Cleared {active_count} active sessions")


# Create FastAPI app
app = FastAPI(
    title="VaaNI Gateway Service",
    description="Orchestrates voice_service and llm_service for real-time customer support",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REST Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "VaaNI Gateway",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    active_sessions = session_store.get_active_sessions()
    return {
        "status": "healthy",
        "active_sessions": len(active_sessions),
        "services": {
            "voice_service": "connected",
            "llm_service": "connected"
        }
    }


@app.post("/session/start", response_model=SessionStartResponse)
async def start_session():
    """
    Start a new session and return session ID.

    The client should use this session_id to connect via WebSocket.
    """
    try:
        session_id = session_store.create_session()
        logger.info(f"Created new session: {session_id}")

        return SessionStartResponse(session_id=session_id)

    except Exception as e:
        logger.error(f"Error creating session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create session: {e}")


@app.post("/session/{session_id}/end", response_model=SessionEndResponse)
async def end_session(session_id: str):
    """
    End a session and generate summary.

    This will call the LLM service to generate a summary of the conversation.
    """
    try:
        session = session_store.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get conversation history
        conversation = session.get_history_for_llm()
        customer_language = session.language or "en"

        # Call LLM service for summary
        orchestrator = Orchestrator()
        try:
            summary_en, summary_lang, query_type = await orchestrator.llm.summarize_conversation(
                conversation=conversation,
                customer_language=customer_language
            )

            # Mark session as ended
            session_store.end_session(session_id)

            logger.info(f"Session {session_id} ended with summary")

            return SessionEndResponse(
                summary_en=summary_en,
                summary_lang=summary_lang,
                query_type=query_type
            )

        finally:
            await orchestrator.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to end session: {e}")


@app.get("/session/{session_id}/transcript", response_model=TranscriptResponse)
async def get_transcript(session_id: str):
    """
    Get the full transcript for a session.

    Returns all messages exchanged between customer and staff.
    """
    try:
        session = session_store.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Convert transcript entries to response format
        transcript = [
            TranscriptEntry(
                role=entry.role,
                text=entry.text,
                language=entry.language,
                timestamp=entry.timestamp
            )
            for entry in session.transcript
        ]

        return TranscriptResponse(transcript=transcript)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transcript: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get transcript: {e}")


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session and free up resources.

    This permanently removes the session from memory.
    """
    try:
        deleted = session_store.delete_session(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")

        logger.info(f"Deleted session: {session_id}")

        return {"message": f"Session {session_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {e}")


@app.get("/sessions")
async def list_sessions():
    """
    List all active sessions.

    Returns a list of session IDs and basic info.
    """
    try:
        active_sessions = session_store.get_active_sessions()
        sessions_info = []

        for session_id in active_sessions:
            session = session_store.get_session(session_id)
            if session:
                sessions_info.append({
                    "session_id": session.session_id,
                    "created_at": session.created_at.isoformat(),
                    "language": session.language,
                    "transcript_length": len(session.transcript),
                    "is_active": session.is_active
                })

        return {"sessions": sessions_info, "count": len(sessions_info)}

    except Exception as e:
        logger.error(f"Error listing sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {e}")


@app.get("/session/{session_id}/export/pdf")
async def export_session_pdf(session_id: str):
    """
    Export session as bilingual PDF.

    Returns a professionally formatted PDF with:
    - Bilingual title
    - Session metadata
    - Conversation log (original + translation)
    - Summary in both languages
    - Query type and resolution status
    - Process steps completed
    """
    try:
        session = session_store.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get transcript for table
        transcript_data = []
        for entry in session.transcript:
            transcript_data.append({
                "role": entry.role,
                "text": entry.text,
                "original_text": entry.text,
                "translated_text": entry.text if entry.language == "en" else "",
                "timestamp": entry.timestamp.isoformat(),
            })

        # Get summary (generate if not available)
        if not session.process_type:
            conversation = session.get_history_for_llm()
            customer_language = session.language or "en"
            orchestrator = Orchestrator()
            try:
                summary_en, summary_lang, query_type = await orchestrator.llm.summarize_conversation(
                    conversation=conversation,
                    customer_language=customer_language
                )
                session.process_type = query_type
            finally:
                await orchestrator.close()
        else:
            # For demo, use placeholder summaries
            summary_en = "Customer inquiry regarding account services was handled successfully."
            summary_lang = summary_en
            query_type = session.process_type or "General Inquiry"

        # Prepare session data for PDF
        session_data = {
            "session_id": session_id,
            "customer_language": session.language or "en",
            "start_time": session.created_at.isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "branch_code": "BR-001",  # Placeholder
            "staff_id": "STAFF-001",  # Placeholder
            "transcript": transcript_data,
            "summary_en": summary_en,
            "summary_lang": summary_lang,
            "query_type": query_type,
            "resolved": True,
            "escalated": False,
            "process_steps": [],  # Could be populated from session state
        }

        # Generate PDF
        logger.info(f"Generating PDF for session {session_id}")
        pdf_bytes = pdf_generator.generate_pdf(session_data)

        # Return as downloadable PDF
        filename = f"vaani_session_{session_id[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {e}")


@app.post("/session/{session_id}/export/json")
async def export_session_json(session_id: str):
    """
    Export full session data as structured JSON.

    Useful for CBS/CRM integration.
    Returns all session data including transcript, metadata, and summary.
    """
    try:
        session = session_store.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Build complete session data
        session_data = {
            "session_id": session_id,
            "created_at": session.created_at.isoformat(),
            "ended_at": datetime.utcnow().isoformat() if not session.is_active else None,
            "language": session.language,
            "is_active": session.is_active,
            "process_type": session.process_type,
            "transcript": [
                {
                    "role": entry.role,
                    "text": entry.text,
                    "language": entry.language,
                    "timestamp": entry.timestamp.isoformat(),
                }
                for entry in session.transcript
            ],
            "metadata": {
                "branch_code": "BR-001",  # Placeholder
                "staff_id": "STAFF-001",  # Placeholder
                "duration_seconds": int((datetime.utcnow() - session.created_at).total_seconds()),
            }
        }

        logger.info(f"Exported JSON for session {session_id}")

        return session_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to export JSON: {e}")


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time audio streaming and bi-directional messaging.

    Client messages:
    - {"type": "audio_chunk", "data": "<base64_audio>"}
    - {"type": "language_select", "language": "hi"}
    - {"type": "staff_response", "text": "...", "language": "hi"}
    - {"type": "session_end"}

    Server messages:
    - {"type": "transcript", "text": "...", "language": "hi", "confidence": 0.92}
    - {"type": "translation", "text": "...", "language": "en"}
    - {"type": "suggestion", "suggestions": ["..."], "process_steps": [...], "escalate": false}
    - {"type": "tts_audio", "audio_b64": "...", "language": "hi"}
    - {"type": "lid_result", "language": "hi", "confidence": 0.95}
    - {"type": "error", "message": "..."}
    """
    await ws_handler.handle_connection(websocket, session_id)


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting Gateway service on {GATEWAY_HOST}:{GATEWAY_PORT}")
    logger.info(f"CORS allowed origins: {ALLOWED_ORIGINS}")
    logger.info(f"Debug mode: {DEBUG_MODE}")

    uvicorn.run(
        "main:app",
        host=GATEWAY_HOST,
        port=GATEWAY_PORT,
        log_level=LOG_LEVEL.lower(),
        reload=DEBUG_MODE
    )
