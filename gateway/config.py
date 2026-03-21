"""Configuration for the gateway service."""

import os
from typing import Optional


# Service URLs (with defaults for local development)
VOICE_SERVICE_URL: str = os.getenv(
    "VOICE_SERVICE_URL",
    "http://voice_service:8001"
)

LLM_SERVICE_URL: str = os.getenv(
    "LLM_SERVICE_URL",
    "http://llm_service:8002"
)

# Gateway configuration
GATEWAY_HOST: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", "8000"))

# CORS configuration
ALLOWED_ORIGINS: list[str] = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

# WebSocket settings
WS_MAX_MESSAGE_SIZE: int = int(os.getenv("WS_MAX_MESSAGE_SIZE", "16777216"))  # 16MB default
WS_TIMEOUT: int = int(os.getenv("WS_TIMEOUT", "30"))  # seconds

# Session settings
SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
MAX_TRANSCRIPT_ENTRIES: int = int(os.getenv("MAX_TRANSCRIPT_ENTRIES", "1000"))

# Processing settings
ENABLE_LID: bool = os.getenv("ENABLE_LID", "true").lower() == "true"
AUTO_TRANSLATE: bool = os.getenv("AUTO_TRANSLATE", "true").lower() == "true"
AUTO_SUGGEST: bool = os.getenv("AUTO_SUGGEST", "true").lower() == "true"

# Default language settings
DEFAULT_CUSTOMER_LANGUAGE: str = os.getenv("DEFAULT_CUSTOMER_LANGUAGE", "en")
STAFF_LANGUAGE: str = os.getenv("STAFF_LANGUAGE", "en")

# Retry settings for service calls
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY_MS: int = int(os.getenv("RETRY_DELAY_MS", "100"))

# Logging
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"


def get_service_url(service_name: str) -> Optional[str]:
    """
    Get service URL by name.
    Useful for dynamic service discovery in the future.
    """
    service_urls = {
        "voice_service": VOICE_SERVICE_URL,
        "llm_service": LLM_SERVICE_URL,
    }
    return service_urls.get(service_name)
