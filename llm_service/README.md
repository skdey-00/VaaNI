# LLM Banking Assistant Service

An AI-powered microservice for banking context awareness and process guidance, built with FastAPI, LangChain, and FAISS.

## Features

- **RAG-based Process Guidance**: Retrieves relevant banking procedures from markdown knowledge base
- **Bilingual Summarization**: Generates session summaries in English and customer's language
- **Session Management**: Stateful conversation tracking with UUID-based sessions
- **Mock Mode**: Test without Ollama using hardcoded realistic responses
- **10 Indian Languages**: Supports Hindi, Tamil, Telugu, Kannada, Malayalam, Marathi, Gujarati, Bengali, Odia

## Banking Processes Covered

1. **Account Opening** - Savings, Current, NRI accounts with RBI compliance
2. **KYC Verification** - e-KYC, offline KYC, document requirements
3. **Loan Enquiry** - Home, Personal, Auto, Gold loans with eligibility assessment
4. **Fixed Deposit Booking** - Regular, Tax-saving, Senior citizen FDs
5. **Remittance** - NEFT, RTGS, IMPS, UPI, International transfers
6. **Complaint Lodging** - Comprehensive complaint handling process

## Quick Start

### Prerequisites

- Python 3.11+
- Ollama with `gemma2:9b` and `nomic-embed-text` models

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Pull Ollama models (if using Ollama)
ollama pull gemma2:9b
ollama pull nomic-embed-text
```

### Running the Service

**Development Mode (Mock Mode - No Ollama Required):**
```bash
# Set environment variable
export MOCK_MODE=true

# Run the service
python main.py
```

**Production Mode (With Ollama):**
```bash
# Set environment variable
export MOCK_MODE=false

# Run the service
python main.py
```

**Using Docker:**
```bash
docker-compose up --build
```

The service will be available at `http://localhost:8001`

## API Endpoints

### Session Management

#### Start Session
```http
POST /session/start
Content-Type: application/json

{
  "customer_id": "CUST123",
  "customer_language": "hi",
  "initial_query": "I want to open a savings account"
}
```

#### End Session
```http
POST /session/end
Content-Type: application/json

{
  "session_id": "uuid-here"
}
```

### Core Endpoints

#### Get Suggestions
```http
POST /suggest
Content-Type: application/json

{
  "session_id": "uuid-here",
  "transcript_en": "Customer wants to know about fixed deposit rates",
  "session_history": [],
  "process_type": "fd_booking"
}
```

**Response:**
```json
{
  "suggestions": [
    "Explain current FD interest rates for different tenures",
    "Inform about premature withdrawal penalties",
    "Explain tax deduction at source (TDS) on interest"
  ],
  "process_steps": [
    {"step": 1, "description": "Discuss FD tenure options", "done": false},
    {"step": 2, "description": "Explain premature withdrawal rules", "done": false}
  ],
  "escalate": false,
  "process_type": "fd_booking"
}
```

#### Summarise Session
```http
POST /summarise
Content-Type: application/json

{
  "session_id": "uuid-here",
  "session_history": [
    {"role": "customer", "text_en": "I want to open a FD", "language": "en"},
    {"role": "staff", "text_en": "Sure, I can help with that", "language": "en"}
  ],
  "customer_language": "hi"
}
```

**Response:**
```json
{
  "summary_en": "Customer enquired about fixed deposit options...",
  "summary_lang": "ग्राहक ने फिक्स्ड डिपॉजिट विकल्पों के बारे में पूछा...",
  "query_type": "Fixed Deposit",
  "resolved": true,
  "key_points": ["...", "..."],
  "action_items": ["..."]
}
```

#### List Processes
```http
GET /processes
```

## Configuration

Edit `config.py` or set environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_HOST` | Ollama service URL | `http://localhost:11434` |
| `MODEL_NAME` | LLM model | `gemma2:9b` |
| `MOCK_MODE` | Use mock responses | `true` |
| `CHUNK_SIZE` | RAG chunk size | `300` |
| `CHUNK_OVERLAP` | RAG chunk overlap | `50` |

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (main.py)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│  RAG  │ │  LLM  │
│ rag.py│ │llm.py │
└───┬───┘ └──┬────┘
    │        │
┌───▼───────▼──┐
│   Ollama     │
│  + FAISS     │
└──────────────┘
```

## Knowledge Base

The `processes/` directory contains comprehensive markdown files for each banking procedure. These are:
- Loaded on startup
- Chunked into 300-token pieces with 50-token overlap
- Indexed using FAISS with `nomic-embed-text` embeddings
- Retrieved at query time for RAG

## Development

### Adding New Processes

1. Create a new markdown file in `processes/`
2. Follow the existing format (numbered steps, clear sections)
3. Restart the service to rebuild the FAISS index

### Testing

```bash
# Run with mock mode (no Ollama needed)
MOCK_MODE=true python main.py

# Test endpoints
curl http://localhost:8001/health
curl http://localhost:8001/processes
```

## License

MIT
