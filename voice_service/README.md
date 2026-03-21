# Voice Service - Multilingual Banking Assistant

A FastAPI microservice that wraps AI4Bharat models for voice-enabled banking in Indian languages.

## Features

- **🎤 ASR** (Automatic Speech Recognition) - Speech-to-text for 12+ Indian languages
- **🌐 Translation** - English ↔ Indian language translation with banking domain awareness
- **🔊 TTS** (Text-to-Speech) - Neural voice synthesis in multiple languages
- **🔍 LID** (Language Identification) - Automatic language detection from audio
- **Mock Mode** - Instant responses for frontend development without GPU

## Supported Languages

| Language | Code | Script |
|----------|------|--------|
| English | `en` | Latin |
| Hindi | `hi` | Devanagari |
| Marathi | `mr` | Devanagari |
| Tamil | `ta` | Tamil |
| Bengali | `bn` | Bengali |
| Telugu | `te` | Telugu |
| Kannada | `kn` | Kannada |
| Malayalam | `ml` | Malayalam |
| Gujarati | `gu` | Gujarati |
| Odia | `or` | Odia |
| Punjabi | `pa` | Gurmukhi |
| Assamese | `as` | Assamese |

## Quick Start

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```

3. **Run with Mock Mode** (no GPU required)
   ```bash
   MOCK_MODE=true python main.py
   ```

4. **Run with actual models** (GPU recommended)
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs`

### Docker

```bash
# Build image
docker build -t voice-service .

# Run with Mock Mode
docker run -p 8000:8000 -e MOCK_MODE=true voice-service

# Run with GPU (needs nvidia-docker)
docker run --gpus all -p 8000:8000 voice-service
```

## API Endpoints

### POST /asr - Speech to Text
```bash
curl -X POST "http://localhost:8000/asr" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_b64": "UklGRiQAAABXQVZF...",
    "language": "hi"
  }'
```

**Response:**
```json
{
  "transcript": "मेरे खाते का बैलेंस बताएं",
  "confidence": 0.95,
  "language": "hi",
  "latency_ms": 245.3,
  "model": "indicwav2vec"
}
```

### POST /translate - Translation
```bash
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What is my account balance?",
    "src": "en",
    "tgt": "hi",
    "use_banking_glossary": true
  }'
```

**Response:**
```json
{
  "translation": "मेरे खाते का बैलेंस क्या है?",
  "source_language": "en",
  "target_language": "hi",
  "direction": "en-indic",
  "latency_ms": 185.6,
  "model": "indictrans2"
}
```

### POST /tts - Text to Speech
```bash
curl -X POST "http://localhost:8000/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "आपका खाता शेष पांच हजार रुपये है",
    "language": "hi",
    "speaker": "female"
  }'
```

**Response:**
```json
{
  "audio_b64": "UklGRiQAAABXQVZF...",
  "duration_ms": 3200,
  "sample_rate": 22050,
  "language": "hi",
  "speaker": "female",
  "latency_ms": 450.2,
  "model": "indicTTS"
}
```

### POST /lid - Language Identification
```bash
curl -X POST "http://localhost:8000/lid" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_b64": "UklGRiQAAABXQVZF..."
  }'
```

**Response:**
```json
{
  "language": "hi",
  "language_name": "Hindi",
  "confidence": 0.92,
  "latency_ms": 35.0,
  "method": "model"
}
```

### GET /languages - Supported Languages
```bash
curl "http://localhost:8000/languages"
```

## Banking Glossary

The service includes a domain-specific glossary with ~50 banking terms to ensure accurate translation of financial terminology:

- **Account**: EMI, NEFT, RTGS, KYC, FD, RD, CBS, PMJDY
- **Cards**: ATM, PIN, DC (Debit Card), CC (Credit Card)
- **Identity**: Aadhaar, PAN, IFSC, MICR
- **Banking**: UPI, IMPS, NEFT, RTGS, QR, POS
- **Loans**: Interest, Principal, Tenure, Collateral, Mortgage
- **Investments**: PPF, EPF, NPS, SIP, NAV, IPO, ETF

Translations are available in Hindi, Marathi, Tamil, and Bengali.

## Performance Targets

| Operation | Target Latency |
|-----------|---------------|
| ASR | < 500ms |
| Translation | < 400ms |
| TTS | < 600ms |

Actual latency is logged and returned in each response.

## Configuration

Set via environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `MOCK_MODE` | `false` | Enable mock responses (instant) |
| `DEVICE` | `cpu` | Device: `cpu` or `cuda` |
| `MODEL_PATH` | `./models` | Path to cached models |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |

## Audio Format

All audio must be:
- **Format**: WAV
- **Sample Rate**: 16000 Hz (16 kHz)
- **Channels**: Mono (1 channel)
- **Encoding**: Base64

Example conversion with ffmpeg:
```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
```

## Architecture

```
voice_service/
├── main.py              # FastAPI app, endpoints, CORS
├── asr.py               # Speech-to-text (IndicASR/Whisper)
├── translate.py         # Translation (IndicTrans2)
├── tts.py               # Text-to-speech (IndicTTS)
├── lid.py               # Language identification (IndicLID)
├── banking_glossary.py  # Banking terminology translations
├── config.py            # Configuration, settings
├── Dockerfile           # Container image
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## License

MIT

## Credits

- **AI4Bharat** - IndicASR, IndicTrans2, IndicTTS, IndicLID models
- **OpenAI** - Whisper model (fallback ASR)
- **FastAPI** - Web framework
