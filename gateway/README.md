# VaaNI Gateway Service

FastAPI-based gateway that orchestrates voice_service and llm_service microservices for real-time customer support.

## Features

- **WebSocket endpoint** for real-time audio streaming and bidirectional messaging
- **REST API** for session lifecycle management
- **Automatic language detection** (LID)
- **Speech-to-text** (ASR) transcription
- **Translation** between customer language and English
- **AI-powered suggestions** from LLM service
- **Text-to-speech** (TTS) for staff responses
- **In-memory session management** with full transcript history

## Architecture

```
Browser → Gateway (WebSocket/REST) → Voice Service (ASR/LID/Translation/TTS)
                                     → LLM Service (Suggestions/Summarization)
```

## Quick Start

### Using Docker Compose

```bash
# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f gateway

# Stop services
docker-compose down
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export VOICE_SERVICE_URL=http://localhost:8001
export LLM_SERVICE_URL=http://localhost:8002

# Run gateway
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

### REST Endpoints

#### Start a Session
```bash
POST /session/start

Response:
{
  "session_id": "uuid-v4"
}
```

#### End a Session
```bash
POST /session/{session_id}/end

Response:
{
  "summary_en": "Session summary in English",
  "summary_lang": "सारांश ग्राहक की भाषा में",
  "query_type": "refund_request"
}
```

#### Get Transcript
```bash
GET /session/{session_id}/transcript

Response:
{
  "transcript": [
    {
      "role": "customer",
      "text": "मैं रिफंड चाहता हूं",
      "language": "hi",
      "timestamp": "2025-01-15T10:30:00Z"
    },
    {
      "role": "staff",
      "text": "I can help you with that",
      "language": "en",
      "timestamp": "2025-01-15T10:30:15Z"
    }
  ]
}
```

#### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "active_sessions": 3,
  "services": {
    "voice_service": "connected",
    "llm_service": "connected"
  }
}
```

### WebSocket Protocol

**Connect to:** `ws://localhost:8000/ws/{session_id}`

#### Client → Server Messages

**Audio Chunk:**
```json
{
  "type": "audio_chunk",
  "data": "base64_encoded_audio_data"
}
```

**Language Selection:**
```json
{
  "type": "language_select",
  "language": "hi"
}
```

**Staff Response:**
```json
{
  "type": "staff_response",
  "text": "Hello, how can I help you?",
  "language": "hi"
}
```

**End Session:**
```json
{
  "type": "session_end"
}
```

#### Server → Client Messages

**Transcript:**
```json
{
  "type": "transcript",
  "text": "मैं रिफंड चाहता हूं",
  "language": "hi",
  "confidence": 0.92
}
```

**Translation:**
```json
{
  "type": "translation",
  "text": "I want a refund",
  "language": "en"
}
```

**AI Suggestions:**
```json
{
  "type": "suggestion",
  "suggestions": [
    "I can process your refund right away",
    "Could you provide your order number?"
  ],
  "process_steps": ["transcription", "translation", "llm_suggestion"],
  "escalate": false
}
```

**TTS Audio:**
```json
{
  "type": "tts_audio",
  "audio_b64": "base64_encoded_audio",
  "language": "hi"
}
```

**Language Detection:**
```json
{
  "type": "lid_result",
  "language": "hi",
  "confidence": 0.95
}
```

**Error:**
```json
{
  "type": "error",
  "message": "Error description"
}
```

## Configuration

Key environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `VOICE_SERVICE_URL` | `http://voice_service:8001` | Voice service endpoint |
| `LLM_SERVICE_URL` | `http://llm_service:8002` | LLM service endpoint |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS allowed origins |
| `ENABLE_LID` | `true` | Enable language detection |
| `AUTO_TRANSLATE` | `true` | Auto-translate to English |
| `AUTO_SUGGEST` | `true` | Auto-generate suggestions |

## Pipeline Flow

### Customer Audio Flow
1. Client sends `audio_chunk`
2. Gateway calls `/lid` (first chunk only) → `lid_result`
3. Gateway calls `/asr` → `transcript`
4. Gateway calls `/translate` → `translation`
5. Gateway calls LLM `/suggest` → `suggestion`

### Staff Response Flow
1. Client sends `staff_response`
2. Gateway calls `/translate` (en → customer_lang)
3. Gateway calls `/tts` → `tts_audio`

## Session Management

Sessions are stored in-memory with:
- Unique session ID (UUID)
- Detected/selected language
- Full transcript history
- Session state (active/ended)
- Creation timestamp

Sessions persist until explicitly deleted via API or server restart.

## Testing

See `test_client.py` for a Python WebSocket client example.

```bash
python test_client.py
```

## Monitoring

The service exposes health checks and metrics at `/health`. For full monitoring, enable the monitoring profile:

```bash
docker-compose --profile monitoring up -d
```

Access Grafana at `http://localhost:3001` (admin/admin).

## Troubleshooting

### Connection Refused
- Ensure voice_service and llm_service are running
- Check service URLs in environment variables

### WebSocket Disconnects
- Check audio chunk size (<16MB)
- Verify session_id is valid
- Check logs for errors

### Empty Translations
- Verify voice_service translation is enabled
- Check language codes are valid
- Review voice_service logs
