# VaaNI Integration Tests

Test suite for the VaaNI multilingual banking assistant.

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_pipeline.py         # Voice/LLM service pipeline tests
├── test_ws.py               # WebSocket integration tests
├── test_summary.py          # Summary and PDF export tests
├── generate_fixtures.py     # Generate test audio fixtures
└── fixtures/
    └── audio/               # Test audio files (generated)
```

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- All services built (`docker-compose build`)

## Running Tests

### Run All Tests

```bash
# Start services
docker-compose up -d

# Run tests
pytest tests/

# Stop services
docker-compose down
```

### Run Specific Test Files

```bash
# Pipeline tests only
pytest tests/test_pipeline.py -v

# WebSocket tests only
pytest tests/test_ws.py -v

# Summary tests only
pytest tests/test_summary.py -v
```

### Run with Markers

```bash
# Skip slow tests
pytest tests/ -m "not slow"

# Integration tests only
pytest tests/ -m integration

# Unit tests only
pytest tests/ -m unit
```

### Generate Audio Fixtures

```bash
# Generate test audio files
python tests/generate_fixtures.py
```

## Test Coverage

### test_pipeline.py
- ✅ ASR endpoint with real audio
- ✅ LID endpoint with real audio
- ✅ Translation endpoint
- ✅ TTS endpoint
- ✅ LLM suggestions endpoint
- ✅ Full pipeline flow

### test_ws.py
- ✅ WebSocket connection
- ✅ Message ordering (lid → transcript → translation → suggestion)
- ✅ Staff response and TTS
- ✅ Session end
- ✅ Multiple audio chunks

### test_summary.py
- ✅ Bilingual summary generation
- ✅ Transcript retrieval
- ✅ PDF export
- ✅ JSON export
- ✅ Session lifecycle
- ✅ Concurrent sessions

## CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    docker-compose up -d
    pytest tests/ -v
    docker-compose down
```

## Troubleshooting

### Tests Fail with Connection Errors
- Ensure services are running: `docker-compose ps`
- Check service health: `curl http://localhost:8000/health`
- Verify ports: 8000 (gateway), 8001 (voice), 8002 (llm)

### Audio Fixtures Missing
```bash
python tests/generate_fixtures.py
```

### Services Not Starting
```bash
docker-compose down -v
docker-compose up --build
```

## Adding New Tests

1. Create `test_<feature>.py` in `tests/`
2. Use fixtures from `conftest.py`
3. Mark with appropriate decorators: `@pytest.mark.integration`
4. Run: `pytest tests/test_<feature>.py -v`
