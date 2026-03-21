"""
Simple test client for Voice Service
Use this to quickly test the API endpoints
"""
import base64
import json
import requests
from typing import Dict


class VoiceServiceClient:
    """Client for testing Voice Service endpoints"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def health_check(self) -> Dict:
        """Check service health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def get_languages(self) -> list:
        """Get supported languages"""
        response = requests.get(f"{self.base_url}/languages")
        return response.json()

    def translate(
        self,
        text: str,
        src: str = "en",
        tgt: str = "hi",
        use_glossary: bool = True
    ) -> Dict:
        """Test translation endpoint"""
        payload = {
            "text": text,
            "src": src,
            "tgt": tgt,
            "use_banking_glossary": use_glossary
        }
        response = requests.post(f"{self.base_url}/translate", json=payload)
        return response.json()

    def text_to_speech(
        self,
        text: str,
        language: str = "hi",
        speaker: str = "female"
    ) -> Dict:
        """Test TTS endpoint"""
        payload = {
            "text": text,
            "language": language,
            "speaker": speaker
        }
        response = requests.post(f"{self.base_url}/tts", json=payload)
        return response.json()

    def speech_to_text(self, audio_b64: str, language: str = "hi") -> Dict:
        """Test ASR endpoint"""
        payload = {
            "audio_b64": audio_b64,
            "language": language
        }
        response = requests.post(f"{self.base_url}/asr", json=payload)
        return response.json()

    def identify_language(self, audio_b64: str) -> Dict:
        """Test LID endpoint"""
        payload = {"audio_b64": audio_b64}
        response = requests.post(f"{self.base_url}/lid", json=payload)
        return response.json()


def create_mock_audio(duration_seconds: float = 2.0) -> str:
    """Create a mock WAV audio for testing"""
    import wave
    import struct
    import io

    sample_rate = 16000
    num_samples = int(sample_rate * duration_seconds)

    # Create WAV file in memory
    audio_io = io.BytesIO()
    with wave.open(audio_io, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes (16-bit)
        wav_file.setframerate(sample_rate)

        # Write simple sine wave
        import math
        for i in range(num_samples):
            value = int(32767 * 0.3 * math.sin(2 * math.pi * 440 * i / sample_rate))
            wav_file.writeframes(struct.pack('<h', value))

    audio_io.seek(0)
    audio_bytes = audio_io.read()
    return base64.b64encode(audio_bytes).decode('utf-8')


def main():
    """Run tests"""
    print("=" * 60)
    print("Voice Service Test Client")
    print("=" * 60)

    client = VoiceServiceClient()

    # Test health
    print("\n1. Health Check")
    print("-" * 40)
    try:
        health = client.health_check()
        print(json.dumps(health, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        return

    # Test languages
    print("\n2. Supported Languages")
    print("-" * 40)
    try:
        langs = client.get_languages()
        print(f"Found {len(langs)} languages:")
        for lang in langs[:5]:
            print(f"  - {lang['name']} ({lang['code']}, {lang['script']})")
        print(f"  ... and {len(langs) - 5} more")
    except Exception as e:
        print(f"Error: {e}")

    # Test translation
    print("\n3. Translation (EN → HI)")
    print("-" * 40)
    try:
        result = client.translate(
            text="What is my account balance?",
            src="en",
            tgt="hi"
        )
        print(f"Source: What is my account balance?")
        print(f"Translation: {result['translation']}")
        print(f"Latency: {result['latency_ms']:.0f}ms")
    except Exception as e:
        print(f"Error: {e}")

    # Test TTS
    print("\n4. Text-to-Speech (HI)")
    print("-" * 40)
    try:
        result = client.text_to_speech(
            text="आपका खाता शेष पांच हजार रुपये है",
            language="hi"
        )
        print(f"Audio duration: {result['duration_ms']}ms")
        print(f"Audio size: {len(result['audio_b64'])} chars (base64)")
        print(f"Latency: {result['latency_ms']:.0f}ms")
    except Exception as e:
        print(f"Error: {e}")

    # Test ASR
    print("\n5. Speech-to-Text (HI)")
    print("-" * 40)
    try:
        mock_audio = create_mock_audio(2.0)
        result = client.speech_to_text(mock_audio, language="hi")
        print(f"Transcript: {result['transcript']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Latency: {result['latency_ms']:.0f}ms")
    except Exception as e:
        print(f"Error: {e}")

    # Test LID
    print("\n6. Language Identification")
    print("-" * 40)
    try:
        mock_audio = create_mock_audio(1.5)
        result = client.identify_language(mock_audio)
        print(f"Detected: {result['language_name']} ({result['language']})")
        print(f"Confidence: {result['confidence']}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
