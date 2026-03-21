"""
Generate synthetic audio demos using TTS.

Creates realistic test audio files in multiple Indian languages
for demoing the VaaNI banking assistant.

Requirements:
    pip install gtts pyttsx3
"""

import os
from pathlib import Path
from typing import List, Dict
import subprocess
import sys


class AudioGenerator:
    """Generate synthetic audio using TTS engines."""

    def __init__(self, output_dir: Path = Path("demo/audio")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_with_gtts(self, text: str, lang: str, filename: str) -> bool:
        """Generate audio using Google TTS (requires internet)."""
        try:
            from gtts import gTTS
            import io

            print(f"🎤 Generating {filename} with gTTS ({lang})...")

            tts = gTTS(text=text, lang=lang, slow=False)
            output_path = self.output_dir / filename

            # Save to MP3
            tts.save(str(output_path))

            # Convert to WAV using ffmpeg (if available)
            wav_path = output_path.with_suffix('.wav')
            try:
                subprocess.run([
                    'ffmpeg', '-y',
                    '-i', str(output_path),
                    '-ar', '16000',  # 16 kHz sample rate
                    '-ac', '1',      # Mono
                    str(wav_path)
                ], check=True, capture_output=True)
                os.remove(output_path)  # Remove MP3
                print(f"✅ Created: {wav_path}")
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"✅ Created: {output_path} (MP3, ffmpeg not available)")
                return True

        except ImportError:
            print("⚠️  gTTS not installed: pip install gtts")
            return False
        except Exception as e:
            print(f"❌ Error generating with gTTS: {e}")
            return False

    def generate_with_pyttsx3(self, text: str, filename: str) -> bool:
        """Generate audio using pyttsx3 (offline)."""
        try:
            import pyttsx3

            print(f"🎤 Generating {filename} with pyttsx3...")

            engine = pyttsx3.init()
            output_path = self.output_dir / filename

            # Save to file
            engine.save_to_file(text, str(output_path))
            engine.runAndWait()

            print(f"✅ Created: {output_path}")
            return True

        except ImportError:
            print("⚠️  pyttsx3 not installed: pip install pyttsx3")
            return False
        except Exception as e:
            print(f"❌ Error generating with pyttsx3: {e}")
            return False

    def generate_all_demos(self):
        """Generate all demo audio files."""

        demos = [
            {
                "name": "hindi_fd_inquiry",
                "text": "मैं एक फिक्स्ड डिपॉजिट खाता खोलना चाहता हूं, क्या प्रक्रिया है?",
                "lang": "hi",
                "method": "gtts"
            },
            {
                "name": "tamil_loan_inquiry",
                "text": "நான் ஒரு கல்வி கடன் வாங்க விரும்புகிறேன், என்ன ஆவணங்கள் தேவை?",
                "lang": "ta",
                "method": "gtts"
            },
            {
                "name": "bengali_account_opening",
                "text": "আমি একটি সঞ্চযী অ্যাকাউন্ট খুলতে চাই, কি কি লাগবে?",
                "lang": "bn",
                "method": "gtts"
            },
            {
                "name": "english_balance_inquiry",
                "text": "I would like to know my account balance please",
                "lang": "en",
                "method": "gtts"
            },
            {
                "name": "spanish_card_inquiry",
                "text": "Quisiera solicitar una tarjeta de débito, ¿cuáles son los requisitos?",
                "lang": "es",
                "method": "gtts"
            },
        ]

        print("\n" + "="*60)
        print("Generating Demo Audio Files")
        print("="*60 + "\n")

        generated = 0
        for demo in demos:
            filename = f"{demo['name']}.wav"

            if demo['method'] == 'gtts':
                success = self.generate_with_gtts(demo['text'], demo['lang'], filename)
            else:
                success = self.generate_with_pyttsx3(demo['text'], filename)

            if success:
                generated += 1

        print("\n" + "="*60)
        print(f"✅ Generated {generated}/{len(demos)} demo files")
        print(f"📁 Output directory: {self.output_dir.absolute()}")
        print("="*60 + "\n")


def main():
    """Main entry point."""
    generator = AudioGenerator()
    generator.generate_all_demos()


if __name__ == "__main__":
    main()
