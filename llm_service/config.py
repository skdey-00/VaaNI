import os
from typing import Literal

# Ollama Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma2:9b")
# Alternative: "llama3.1:8b"

# Mock Mode - returns hardcoded responses for testing without Ollama
MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"

# RAG Configuration
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
FAISS_INDEX_PATH = "faiss_index"

# Session Configuration
SESSION_TIMEOUT_MINUTES = 30

# Supported Languages for Banking
SUPPORTED_LANGUAGES: list[Literal["en", "hi", "ta", "te", "kn", "ml", "mr", "gu", "bn", "or"]] = [
    "en", "hi", "ta", "te", "kn", "ml", "mr", "gu", "bn", "or"
]

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "gu": "Gujarati",
    "bn": "Bengali",
    "or": "Odia"
}

# System Prompt
SYSTEM_PROMPT = """You are an assistant helping Indian bank branch staff. The customer is speaking {language}.

Your role is to:
1. Provide helpful, concise suggestions to assist the bank staff
2. Guide them through the correct banking procedure step by step
3. Identify when escalation to a supervisor is needed
4. Use ONLY the provided context - do not invent policies or procedures

Respond with valid JSON only:
{{
  "suggestions": ["suggestion 1", "suggestion 2"],
  "process_steps": [
    {{"step": 1, "description": "Step description", "done": false}},
    {{"step": 2, "description": "Step description", "done": true}}
  ],
  "escalate": false,
  "reasoning": "Brief explanation if escalate is true"
}}

Be concise. Use simple English. Do not invent policy — only use the provided context."""
