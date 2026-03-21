"""
Generate test audio fixtures for integration tests.

Creates 1-second WAV files with synthetic audio patterns
that simulate real speech for testing purposes.
"""

import wave
import struct
import math
from pathlib import Path


def generate_sine_wave(duration_seconds: int, frequency: int = 440) -> bytes:
    """Generate a simple sine wave audio pattern."""
    sample_rate = 16000  # 16 kHz sample rate
    num_samples = duration_seconds * sample_rate

    audio_data = []
    for i in range(num_samples):
        # Generate sine wave with some variation
        value = math.sin(2 * math.pi * frequency * i / sample_rate)
        # Add some harmonics for more natural sound
        value += 0.3 * math.sin(2 * math.pi * frequency * 2 * i / sample_rate)
        value += 0.1 * math.sin(2 * math.pi * frequency * 3 * i / sample_rate)

        # Convert to 16-bit PCM
        sample = int(value * 16000)  # Amplitude
        audio_data.extend(struct.pack('<h', sample))

    return bytes(audio_data)


def create_wav_file(filename: Path, duration_seconds: int = 1, frequency: int = 440):
    """Create a WAV file with generated audio."""
    filename.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(filename), 'w') as wav_file:
        # Set WAV file parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
        wav_file.setframerate(16000)  # 16 kHz sample rate

        # Generate and write audio data
        audio_data = generate_sine_wave(duration_seconds, frequency)
        wav_file.writeframes(audio_data)

    print(f"Created: {filename}")


def generate_all_fixtures():
    """Generate all test audio fixtures."""
    fixtures_dir = Path(__file__).parent / "fixtures" / "audio"

    print("Generating audio fixtures...")

    # Hindi customer audio (simulating speech pattern)
    create_wav_file(
        fixtures_dir / "hindi_customer_1s.wav",
        duration_seconds=1,
        frequency=300  # Lower frequency for male voice simulation
    )

    # English customer audio
    create_wav_file(
        fixtures_dir / "english_customer_1s.wav",
        duration_seconds=1,
        frequency=400  # Higher frequency for female voice simulation
    )

    # Tamil customer audio
    create_wav_file(
        fixtures_dir / "tamil_customer_1s.wav",
        duration_seconds=1,
        frequency=350
    )

    # Silence for padding
    create_wav_file(
        fixtures_dir / "silence_1s.wav",
        duration_seconds=1,
        frequency=0  # Will create minimal noise
    )

    print(f"\n✅ All fixtures generated in: {fixtures_dir}")


if __name__ == "__main__":
    generate_all_fixtures()
