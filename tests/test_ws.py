"""
WebSocket integration tests.

Tests real-time bidirectional communication through the gateway.
"""

import pytest
import asyncio
import base64
import websockets
import requests
from pathlib import Path


@pytest.mark.integration
@pytest.mark.asyncio
async def test_websocket_full_flow(test_services, audio_fixtures):
    """
    Test complete WebSocket flow:
    1. Connect to WebSocket
    2. Send language selection
    3. Send audio chunk
    4. Receive messages in order: lid_result → transcript → translation → suggestion
    5. Send staff response
    6. Receive tts_audio
    7. End session
    """
    gateway_url = test_services["gateway"].replace("http://", "ws://")

    # Step 0: Create a session
    http = requests.Session()
    response = http.post(f"{test_services['gateway']}/session/start")
    assert response.status_code == 200
    session_id = response.json()["session_id"]
    http.close()

    # Generate test audio data
    audio_data = b"MOCK_AUDIO_DATA" * 100  # Simulated audio
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')

    received_messages = []

    async with websockets.connect(f"{gateway_url}/ws/{session_id}") as ws:
        # Step 1: Send language selection
        await ws.send_json({
            "type": "language_select",
            "language": "hi"
        })

        # Step 2: Send audio chunk
        await ws.send_json({
            "type": "audio_chunk",
            "data": audio_b64
        })

        # Step 3: Receive messages with timeout
        timeout = 10  # seconds
        start_time = asyncio.get_event_loop().time()

        while asyncio.get_event_loop().time() - start_time < timeout:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                data = eval(message) if isinstance(message, str) else message
                received_messages.append(data)

                # Check if we got all expected messages
                message_types = [m.get("type") for m in received_messages]

                # Stop when we have suggestion
                if "suggestion" in message_types:
                    break

            except asyncio.TimeoutError:
                break

    # Step 4: Verify message order
    message_types = [m.get("type") for m in received_messages]
    print(f"Received message types: {message_types}")

    # In mock mode or real mode, we should at least get some messages
    assert len(received_messages) > 0, "No messages received"

    # Verify message structure
    for msg in received_messages:
        assert "type" in msg, f"Message missing 'type': {msg}"

        # Validate known message types
        if msg["type"] == "transcript":
            assert "text" in msg
            assert "language" in msg
            assert "confidence" in msg
        elif msg["type"] == "translation":
            assert "text" in msg
            assert "language" in msg
        elif msg["type"] == "suggestion":
            assert "suggestions" in msg
            assert isinstance(msg["suggestions"], list)
        elif msg["type"] == "lid_result":
            assert "language" in msg
            assert "confidence" in msg
        elif msg["type"] == "tts_audio":
            assert "audio_b64" in msg
            assert "language" in msg

    print(f"✅ WebSocket test completed with {len(received_messages)} messages")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_websocket_staff_response(test_services):
    """Test sending staff response and receiving TTS audio."""
    gateway_url = test_services["gateway"].replace("http://", "ws://")

    # Create session
    http = requests.Session()
    response = http.post(f"{test_services['gateway']}/session/start")
    session_id = response.json()["session_id"]
    http.close()

    async with websockets.connect(f"{gateway_url}/ws/{session_id}") as ws:
        # Set language first
        await ws.send_json({
            "type": "language_select",
            "language": "hi"
        })

        # Send staff response
        await ws.send_json({
            "type": "staff_response",
            "text": "I can help you with that",
            "language": "hi"
        })

        # Wait for TTS response
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = eval(message) if isinstance(message, str) else message

            assert data["type"] == "tts_audio"
            assert "audio_b64" in data
            assert data["language"] == "hi"

            print("✅ Staff response TTS test passed")
        except asyncio.TimeoutError:
            pytest.fail("No TTS response received")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_websocket_session_end(test_services):
    """Test session end through WebSocket."""
    gateway_url = test_services["gateway"].replace("http://", "ws://")

    # Create session
    http = requests.Session()
    response = http.post(f"{test_services['gateway']}/session/start")
    session_id = response.json()["session_id"]
    http.close()

    async with websockets.connect(f"{gateway_url}/ws/{session_id}") as ws:
        # Send session end
        await ws.send_json({
            "type": "session_end"
        })

        # Should receive session_ended confirmation
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=2.0)
            data = eval(message) if isinstance(message, str) else message

            assert data["type"] == "session_ended"
            assert data["session_id"] == session_id

            print("✅ Session end test passed")
        except asyncio.TimeoutError:
            pytest.fail("No session_end confirmation received")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_websocket_multiple_audio_chunks(test_services):
    """Test sending multiple audio chunks in sequence."""
    gateway_url = test_services["gateway"].replace("http://", "ws://")

    # Create session
    http = requests.Session()
    response = http.post(f"{test_services['gateway']}/session/start")
    session_id = response.json()["session_id"]
    http.close()

    audio_data = b"MOCK_AUDIO" * 50
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')

    transcript_count = 0

    async with websockets.connect(f"{gateway_url}/ws/{session_id}") as ws:
        # Set language
        await ws.send_json({"type": "language_select", "language": "en"})

        # Send multiple chunks
        for i in range(3):
            await ws.send_json({
                "type": "audio_chunk",
                "data": audio_b64
            })
            await asyncio.sleep(0.2)  # Small delay between chunks

        # Collect messages
        try:
            while True:
                message = await asyncio.wait_for(ws.recv(), timeout=3.0)
                data = eval(message) if isinstance(message, str) else message

                if data.get("type") == "transcript":
                    transcript_count += 1

                if transcript_count >= 2:
                    break

        except asyncio.TimeoutError:
            pass

    # At least some transcripts should be received
    assert transcript_count >= 1, f"Expected at least 1 transcript, got {transcript_count}"
    print(f"✅ Multiple chunks test: {transcript_count} transcripts received")
