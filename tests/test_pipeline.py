"""
Pipeline integration tests.

Tests the complete pipeline from voice_service through llm_service
using real audio fixtures.
"""

import pytest
import base64
import requests
from pathlib import Path


# Test data
@pytest.fixture
def hindi_audio_base64(audio_fixtures):
    """Load Hindi audio fixture and return as base64."""
    # First, ensure fixture exists
    audio_file = audio_fixtures / "hindi_customer_1s.wav"

    if not audio_file.exists():
        pytest.skip(f"Audio fixture not found: {audio_file}")

    with open(audio_file, 'rb') as f:
        audio_data = f.read()
        return base64.b64encode(audio_data).decode('utf-8')


@pytest.mark.integration
def test_voice_service_asr(test_services, http_client, hindi_audio_base64):
    """Test ASR endpoint with real Hindi audio."""
    voice_url = test_services["voice_service"]

    # Call ASR endpoint
    response = http_client.post(
        f"{voice_url}/asr",
        json={
            "audio_data": hindi_audio_base64,
            "language": "hi"  # Provide language for ASR
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Assert response shape
    assert "text" in data
    assert "language" in data
    assert "confidence" in data

    # Assert types
    assert isinstance(data["text"], str)
    assert isinstance(data["language"], str)
    assert isinstance(data["confidence"], (int, float))
    assert 0 <= data["confidence"] <= 1

    print(f"✅ ASR Result: {data['text']} (confidence: {data['confidence']})")


@pytest.mark.integration
def test_voice_service_lid(test_services, http_client, hindi_audio_base64):
    """Test LID endpoint with real Hindi audio."""
    voice_url = test_services["voice_service"]

    # Call LID endpoint
    response = http_client.post(
        f"{voice_url}/lid",
        json={
            "audio_data": hindi_audio_base64
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Assert response shape
    assert "language" in data
    assert "confidence" in data

    # Assert types
    assert isinstance(data["language"], str)
    assert len(data["language"]) == 2  # ISO 639-1 code
    assert isinstance(data["confidence"], (int, float))
    assert 0 <= data["confidence"] <= 1

    print(f"✅ LID Result: {data['language']} (confidence: {data['confidence']})")


@pytest.mark.integration
def test_voice_service_translation(test_services, http_client):
    """Test translation endpoint."""
    voice_url = test_services["voice_service"]

    # Call translation endpoint
    response = http_client.post(
        f"{voice_url}/translate",
        json={
            "text": "मैं अपने खाते का बैलेंस जानना चाहता हूं",
            "source_language": "hi",
            "target_language": "en"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Assert response shape
    assert "translated_text" in data
    assert "source_language" in data
    assert "target_language" in data

    # Assert values
    assert data["source_language"] == "hi"
    assert data["target_language"] == "en"
    assert len(data["translated_text"]) > 0

    print(f"✅ Translation: {data['translated_text']}")


@pytest.mark.integration
def test_voice_service_tts(test_services, http_client):
    """Test TTS endpoint."""
    voice_url = test_services["voice_service"]

    # Call TTS endpoint
    response = http_client.post(
        f"{voice_url}/tts",
        json={
            "text": "Hello, how can I help you today?",
            "language": "en"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Assert response shape
    assert "audio_data" in data
    assert "language" in data

    # Assert audio_data is valid base64
    try:
        audio_bytes = base64.b64decode(data["audio_data"])
        assert len(audio_bytes) > 100  # At least some audio data
    except Exception as e:
        pytest.fail(f"Invalid base64 audio data: {e}")

    print(f"✅ TTS generated {len(data['audio_data'])} chars of base64 audio")


@pytest.mark.integration
def test_llm_service_suggestions(test_services, http_client):
    """Test LLM suggestions endpoint."""
    llm_url = test_services["llm_service"]

    # Call suggestions endpoint
    response = http_client.post(
        f"{llm_url}/suggest",
        json={
            "query": "I want to open a fixed deposit account",
            "conversation_history": [],
            "customer_language": "en"
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Assert response shape
    assert "suggestions" in data
    assert "process_steps" in data
    assert "escalate" in data

    # Assert types
    assert isinstance(data["suggestions"], list)
    assert isinstance(data["process_steps"], list)
    assert isinstance(data["escalate"], bool)

    # Assert content
    assert len(data["suggestions"]) > 0
    assert all(isinstance(s, str) for s in data["suggestions"])

    print(f"✅ LLM Suggestions: {data['suggestions']}")


@pytest.mark.integration
def test_full_pipeline_flow(test_services, http_client, hindi_audio_base64):
    """Test complete pipeline: ASR → Translation → LLM → TTS."""
    voice_url = test_services["voice_service"]
    llm_url = test_services["llm_service"]

    # Step 1: LID (detect language)
    lid_response = http_client.post(
        f"{voice_url}/lid",
        json={"audio_data": hindi_audio_base64}
    )
    assert lid_response.status_code == 200
    lid_data = lid_response.json()
    detected_language = lid_data["language"]
    print(f"Step 1 - LID: {detected_language}")

    # Step 2: ASR (transcribe)
    asr_response = http_client.post(
        f"{voice_url}/asr",
        json={"audio_data": hindi_audio_base64, "language": detected_language}
    )
    assert asr_response.status_code == 200
    asr_data = asr_response.json()
    transcript = asr_data["text"]
    print(f"Step 2 - ASR: {transcript}")

    # Step 3: Translation
    if detected_language != "en":
        trans_response = http_client.post(
            f"{voice_url}/translate",
            json={
                "text": transcript,
                "source_language": detected_language,
                "target_language": "en"
            }
        )
        assert trans_response.status_code == 200
        trans_data = trans_response.json()
        translated_text = trans_data["translated_text"]
        print(f"Step 3 - Translation: {translated_text}")
    else:
        translated_text = transcript

    # Step 4: LLM Suggestions
    llm_response = http_client.post(
        f"{llm_url}/suggest",
        json={
            "query": translated_text,
            "conversation_history": [],
            "customer_language": detected_language
        }
    )
    assert llm_response.status_code == 200
    llm_data = llm_response.json()
    print(f"Step 4 - Suggestions: {llm_data['suggestions']}")

    # Step 5: TTS (generate response audio)
    if llm_data["suggestions"]:
        tts_response = http_client.post(
            f"{voice_url}/tts",
            json={
                "text": llm_data["suggestions"][0],
                "language": detected_language
            }
        )
        assert tts_response.status_code == 200
        tts_data = tts_response.json()
        assert "audio_data" in tts_data
        print(f"Step 5 - TTS: Generated {len(tts_data['audio_data'])} chars")

    print("✅ Full pipeline completed successfully!")
