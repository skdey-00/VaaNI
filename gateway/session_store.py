"""In-memory session store for managing active sessions."""

from typing import Dict, List, Optional
from datetime import datetime
import uuid
from models import TranscriptEntry


class Session:
    """Represents an active session with a customer."""

    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.created_at: datetime = datetime.utcnow()
        self.language: Optional[str] = None  # Customer's detected/selected language
        self.transcript: List[TranscriptEntry] = []  # Conversation history
        self.process_type: Optional[str] = None  # Query classification
        self.is_active: bool = True
        self.lid_detected: bool = False  # Whether LID has been performed

    def add_transcript_entry(self, role: str, text: str, language: str) -> None:
        """Add an entry to the transcript."""
        entry = TranscriptEntry(
            role=role,
            text=text,
            language=language,
            timestamp=datetime.utcnow()
        )
        self.transcript.append(entry)

    def get_history_for_llm(self) -> List[dict]:
        """Get conversation history formatted for LLM service."""
        return [
            {
                "role": entry.role,
                "text": entry.text,
                "language": entry.language,
                "timestamp": entry.timestamp.isoformat()
            }
            for entry in self.transcript
        ]

    def end_session(self) -> None:
        """Mark session as ended."""
        self.is_active = False


class SessionStore:
    """In-memory store for active sessions."""

    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = Session(session_id)
        return session_id

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID. Returns True if session existed."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def end_session(self, session_id: str) -> bool:
        """Mark session as ended. Returns True if session existed."""
        session = self.get_session(session_id)
        if session:
            session.end_session()
            return True
        return False

    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return [sid for sid, session in self._sessions.items() if session.is_active]

    def cleanup_inactive_sessions(self) -> int:
        """Remove all inactive sessions and return count of removed sessions."""
        to_delete = [sid for sid, session in self._sessions.items() if not session.is_active]
        for sid in to_delete:
            del self._sessions[sid]
        return len(to_delete)


# Global session store instance
session_store = SessionStore()
