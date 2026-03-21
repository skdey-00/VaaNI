"""
Pytest configuration and fixtures for VaaNI integration tests.

Fixtures:
- test_services: Manages docker-compose lifecycle
- test_client: HTTP client for API calls
- ws_client: WebSocket client for real-time testing
- audio_fixtures: Path to test audio files
"""

import os
import sys
import time
import subprocess
import signal
import pytest
import requests
import websockets
import websockets.client
from pathlib import Path
from typing import Generator, AsyncGenerator

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "gateway"))
sys.path.insert(0, str(PROJECT_ROOT / "voice_service"))
sys.path.insert(0, str(PROJECT_ROOT / "llm_service"))


# Service URLs
GATEWAY_URL = "http://localhost:8000"
VOICE_SERVICE_URL = "http://localhost:8001"
LLM_SERVICE_URL = "http://localhost:8002"
WS_URL = "ws://localhost:8000"


@pytest.fixture(scope="session")
def docker_compose():
    """Start services using docker-compose before tests, stop after."""
    compose_file = PROJECT_ROOT / "docker-compose.yml"
    compose_env = os.environ.copy()
    compose_env["MOCK_MODE"] = "false"  # Use real services for integration tests

    # Start docker-compose
    print("\n🐳 Starting Docker services...")
    proc = subprocess.Popen(
        ["docker-compose", "up", "-d"],
        cwd=PROJECT_ROOT,
        env=compose_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for compose to start
    proc.wait()
    if proc.returncode != 0:
        stderr = proc.stderr.read().decode()
        pytest.fail(f"Failed to start docker-compose: {stderr}")

    # Wait for services to be healthy
    print("⏳ Waiting for services to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            # Check all services
            r = requests.get(f"{GATEWAY_URL}/health", timeout=2)
            if r.status_code == 200:
                print("✅ Gateway is ready")
                break
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                time.sleep(2)
            else:
                pytest.fail("Services did not become ready in time")

    yield

    # Stop services after tests
    print("\n🛑 Stopping Docker services...")
    subprocess.run(
        ["docker-compose", "down", "-v"],
        cwd=PROJECT_ROOT,
        env=compose_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print("✅ Services stopped")


@pytest.fixture(scope="session")
def test_services(docker_compose):
    """Ensure services are running (depends on docker_compose)."""
    # Additional health checks if needed
    time.sleep(1)
    yield {
        "gateway": GATEWAY_URL,
        "voice_service": VOICE_SERVICE_URL,
        "llm_service": LLM_SERVICE_URL,
    }


@pytest.fixture
def http_client():
    """HTTP client for making API requests."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


@pytest.fixture
def audio_fixtures():
    """Path to test audio fixtures."""
    fixtures_dir = PROJECT_ROOT / "tests" / "fixtures" / "audio"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    yield fixtures_dir


@pytest.fixture
async def websocket_client():
    """WebSocket client for testing real-time communication."""
    ws = None

    async def connect(session_id: str):
        nonlocal ws
        uri = f"{WS_URL}/ws/{session_id}"
        ws = await websockets.client.connect(uri)
        return ws

    async def disconnect():
        nonlocal ws
        if ws:
            await ws.close()

    yield {"connect": connect, "disconnect": disconnect}

    # Cleanup
    if ws:
        await ws.close()


@pytest.fixture
async def test_session(http_client):
    """Create a test session and cleanup after."""
    session_id = None

    # Create session
    response = http_client.post(f"{GATEWAY_URL}/session/start")
    assert response.status_code == 200
    data = response.json()
    session_id = data["session_id"]

    yield session_id

    # Cleanup: end and delete session
    if session_id:
        http_client.post(f"{GATEWAY_URL}/session/{session_id}/end")
        http_client.delete(f"{GATEWAY_URL}/session/{session_id}")


@pytest.fixture
def mock_mode(monkeypatch):
    """Enable mock mode for tests."""
    monkeypatch.setenv("MOCK_MODE", "true")
    monkeypatch.setenv("VITE_MOCK_MODE", "true")
    yield


# Skip tests if services are not running
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may require Docker)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "requires_gpu: marks tests that require GPU"
    )


def pytest_collection_modifyitems(config, items):
    """Add markers to tests automatically."""
    for item in items:
        # Mark all tests in tests/ as integration tests
        if "tests/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
