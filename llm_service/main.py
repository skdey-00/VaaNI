from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import json

from config import SUPPORTED_LANGUAGES, LANGUAGE_NAMES
from rag import get_rag_service
from llm import get_llm_client
from summariser import get_summariser

# Initialize FastAPI app
app = FastAPI(
    title="LLM Banking Assistant Service",
    description="AI-powered banking context awareness and process guidance",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage
sessions: Dict[str, Dict] = {}


# Pydantic models
class SessionStart(BaseModel):
    customer_id: Optional[str] = None
    customer_language: str = "en"
    initial_query: Optional[str] = None


class SessionEnd(BaseModel):
    session_id: str


class SuggestRequest(BaseModel):
    session_id: str
    transcript_en: str
    session_history: Optional[List[Dict]] = []
    process_type: Optional[str] = None


class SummariseRequest(BaseModel):
    session_id: str
    session_history: List[Dict]
    customer_language: str = "en"


# Session management endpoints
@app.post("/session/start")
async def start_session(request: SessionStart):
    """Start a new banking session."""
    session_id = str(uuid.uuid4())

    # Validate language
    if request.customer_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language. Supported: {', '.join(SUPPORTED_LANGUAGES)}"
        )

    sessions[session_id] = {
        "session_id": session_id,
        "customer_id": request.customer_id,
        "customer_language": request.customer_language,
        "initial_query": request.initial_query,
        "started_at": datetime.now(),
        "last_activity": datetime.now(),
        "history": [],
        "status": "active"
    }

    # Add initial query to history if provided
    if request.initial_query:
        sessions[session_id]["history"].append({
            "role": "customer",
            "text": request.initial_query,
            "text_en": request.initial_query,
            "language": request.customer_language,
            "timestamp": datetime.now().isoformat()
        })

    return {
        "session_id": session_id,
        "customer_language": request.customer_language,
        "language_name": LANGUAGE_NAMES.get(request.customer_language, "Unknown"),
        "started_at": sessions[session_id]["started_at"].isoformat(),
        "status": "active"
    }


@app.post("/session/end")
async def end_session(request: SessionEnd):
    """End a banking session."""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[request.session_id]
    session["status"] = "ended"
    session["ended_at"] = datetime.now().isoformat()

    return {
        "session_id": request.session_id,
        "status": "ended",
        "duration_minutes": (
            datetime.fromisoformat(session["ended_at"]) - session["started_at"]
        ).total_seconds() / 60
    }


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]

    # Check if session has timed out
    if datetime.now() - session["last_activity"] > timedelta(minutes=30):
        session["status"] = "timeout"

    return {
        "session_id": session["session_id"],
        "customer_id": session.get("customer_id"),
        "customer_language": session["customer_language"],
        "status": session["status"],
        "started_at": session["started_at"].isoformat(),
        "history_count": len(session["history"])
    }


# Core endpoints
@app.post("/suggest")
async def suggest(request: SuggestRequest):
    """Get AI-powered suggestions for the current interaction."""

    # Validate session
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[request.session_id]
    session["last_activity"] = datetime.now()

    # Get RAG context
    rag_service = get_rag_service()
    context = ""
    detected_process = request.process_type

    # If process type not specified, try to detect it from transcript
    if not detected_process:
        all_text = request.transcript_en + " " + " ".join([
            h.get("text_en", "") for h in request.session_history
        ])
        detected_process = rag_service._detect_query_type(all_text)

    # Retrieve relevant context
    if detected_process:
        context = rag_service.get_context(detected_process, k=3)

    # Get LLM response
    llm_client = get_llm_client()
    llm_response = await llm_client.generate(
        prompt=request.transcript_en,
        context=context,
        language=session["customer_language"]
    )

    # Update session history
    session["history"].append({
        "role": "customer",
        "text": request.transcript_en,
        "text_en": request.transcript_en,
        "language": session["customer_language"],
        "timestamp": datetime.now().isoformat()
    })

    # Format process steps
    process_steps = llm_response.get("process_steps", [])
    if not process_steps and detected_process:
        # If LLM didn't return steps, try to get from RAG
        process_info = rag_service.retrieve(f"{detected_process} steps", k=1)
        if process_info:
            # Parse steps from the retrieved document
            lines = process_info[0].split("\n")
            step_num = 1
            for line in lines:
                line = line.strip()
                if line and any(line.startswith(f"{i}.") for i in range(1, 100)):
                    process_steps.append({
                        "step": step_num,
                        "description": line,
                        "done": False
                    })
                    step_num += 1

    return {
        "session_id": request.session_id,
        "suggestions": llm_response.get("suggestions", []),
        "process_steps": process_steps,
        "escalate": llm_response.get("escalate", False),
        "process_type": detected_process or "general",
        "reasoning": llm_response.get("reasoning", ""),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/summarise")
async def summarise(request: SummariseRequest):
    """Generate a bilingual summary of the session."""

    # Validate session
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get summariser
    summariser = get_summariser()

    # Generate summary
    summary = await summariser.summarise(
        session_history=request.session_history,
        customer_language=request.customer_language
    )

    return {
        "session_id": request.session_id,
        "summary_en": summary.get("summary_en", ""),
        "summary_lang": summary.get("summary_lang", ""),
        "query_type": summary.get("query_type", "General Enquiry"),
        "resolved": summary.get("resolved", False),
        "key_points": summary.get("key_points", []),
        "action_items": summary.get("action_items", []),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/processes")
async def list_processes():
    """List all available banking processes."""
    rag_service = get_rag_service()
    processes = rag_service.get_all_processes()
    return {
        "processes": processes,
        "count": len(processes)
    }


@app.get("/processes/{process_id}")
async def get_process_details(process_id: str):
    """Get details of a specific process."""
    rag_service = get_rag_service()
    all_processes = rag_service.get_all_processes()

    for process in all_processes:
        if process["id"] == process_id:
            # Retrieve the full content
            from pathlib import Path
            md_file = Path("processes") / f"{process_id}.md"
            if md_file.exists():
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {
                    **process,
                    "content": content
                }

    raise HTTPException(status_code=404, detail="Process not found")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "llm_service",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len([s for s in sessions.values() if s["status"] == "active"])
    }


# Cleanup expired sessions
@app.on_event("startup")
async def startup():
    """Initialize RAG service on startup."""
    print("Initializing RAG service...")
    rag_service = get_rag_service()
    print(f"RAG service initialized. Loaded {len(rag_service.get_all_processes())} processes.")


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
