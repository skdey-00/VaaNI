"""
Test WebSocket client for VaaNI Gateway Service.

This script demonstrates how to connect to the gateway and test various message flows.
"""

import asyncio
import json
import base64
import websockets
import argparse
from typing import Optional


class GatewayTestClient:
    """Test client for gateway WebSocket."""

    def __init__(self, gateway_url: str = "ws://localhost:8000"):
        self.gateway_url = gateway_url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.session_id: Optional[str] = None

    async def start_session(self) -> str:
        """Start a new session via REST API."""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.gateway_url.replace('ws', 'http')}/session/start") as resp:
                data = await resp.json()
                self.session_id = data["session_id"]
                print(f"✓ Started session: {self.session_id}")
                return self.session_id

    async def connect(self, session_id: str):
        """Connect to WebSocket."""
        uri = f"{self.gateway_url}/ws/{session_id}"
        self.websocket = await websockets.connect(uri)
        print(f"✓ Connected to {uri}")

        # Start listening for messages
        asyncio.create_task(self.listen())

    async def listen(self):
        """Listen for messages from server."""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            print("✗ Connection closed")

    async def handle_message(self, data: dict):
        """Handle incoming message from server."""
        msg_type = data.get("type")

        if msg_type == "transcript":
            print(f"\n📝 Transcript: {data['text']}")
            print(f"   Language: {data['language']}, Confidence: {data['confidence']:.2f}")

        elif msg_type == "translation":
            print(f"\n🌐 Translation: {data['text']}")
            print(f"   Language: {data['language']}")

        elif msg_type == "suggestion":
            print(f"\n💡 Suggestions:")
            for i, suggestion in enumerate(data['suggestions'], 1):
                print(f"   {i}. {suggestion}")
            if data['escalate']:
                print("   ⚠️  ESCALATION RECOMMENDED")

        elif msg_type == "lid_result":
            print(f"\n🔍 Language Detected: {data['language']}")
            print(f"   Confidence: {data['confidence']:.2f}")

        elif msg_type == "tts_audio":
            audio_len = len(data['audio_b64'])
            print(f"\n🔊 TTS Audio received ({audio_len} chars base64)")

        elif msg_type == "error":
            print(f"\n❌ Error: {data['message']}")

        elif msg_type == "session_ended":
            print(f"\n✓ Session {data['session_id']} ended")

        else:
            print(f"\n? Unknown message type: {msg_type}")

    async def send_audio(self, audio_data: str):
        """Send audio chunk."""
        message = {
            "type": "audio_chunk",
            "data": audio_data
        }
        await self.websocket.send(json.dumps(message))
        print("📤 Sent audio chunk")

    async def select_language(self, language: str):
        """Select language."""
        message = {
            "type": "language_select",
            "language": language
        }
        await self.websocket.send(json.dumps(message))
        print(f"📤 Selected language: {language}")

    async def send_staff_response(self, text: str, language: str):
        """Send staff response."""
        message = {
            "type": "staff_response",
            "text": text,
            "language": language
        }
        await self.websocket.send(json.dumps(message))
        print(f"📤 Sent staff response: {text[:50]}...")

    async def end_session(self):
        """End session."""
        message = {
            "type": "session_end"
        }
        await self.websocket.send(json.dumps(message))
        print("📤 Sent session end")

    async def close(self):
        """Close connection."""
        if self.websocket:
            await self.websocket.close()


def create_dummy_audio(text: str = "Hello") -> str:
    """Create dummy base64 audio data (for testing only)."""
    # In production, you would record actual audio
    dummy_data = text.encode() * 100  # Pad to create some data
    return base64.b64encode(dummy_data).decode()


async def test_scenario_1():
    """Test: Language selection + audio processing."""
    print("\n" + "="*60)
    print("TEST SCENARIO 1: Language Selection + Audio")
    print("="*60)

    client = GatewayTestClient()

    try:
        # Start session
        await client.start_session()

        # Connect
        await client.connect(client.session_id)

        # Select language
        await client.select_language("hi")
        await asyncio.sleep(1)

        # Send audio (dummy)
        audio_data = create_dummy_audio("मैं रिफंड चाहता हूं")
        await client.send_audio(audio_data)
        await asyncio.sleep(3)

        # End session
        await client.end_session()
        await asyncio.sleep(1)

    finally:
        await client.close()


async def test_scenario_2():
    """Test: Staff response."""
    print("\n" + "="*60)
    print("TEST SCENARIO 2: Staff Response")
    print("="*60)

    client = GatewayTestClient()

    try:
        # Start session
        await client.start_session()

        # Connect
        await client.connect(client.session_id)

        # Select language
        await client.select_language("es")
        await asyncio.sleep(1)

        # Send staff response
        await client.send_staff_response(
            "I can help you with your refund request.",
            "es"
        )
        await asyncio.sleep(3)

        # End session
        await client.end_session()
        await asyncio.sleep(1)

    finally:
        await client.close()


async def test_interactive():
    """Interactive test mode."""
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    print("\nCommands:")
    print("  1 - Select language")
    print("  2 - Send audio (dummy)")
    print("  3 - Send staff response")
    print("  4 - End session")
    print("  q - Quit")

    client = GatewayTestClient()

    try:
        # Start session
        await client.start_session()
        await client.connect(client.session_id)

        while True:
            try:
                cmd = input("\n> ").strip().lower()

                if cmd == "1":
                    lang = input("Enter language code (e.g., hi, es, en): ").strip()
                    await client.select_language(lang)

                elif cmd == "2":
                    await client.send_audio(create_dummy_audio())

                elif cmd == "3":
                    text = input("Enter response text: ").strip()
                    lang = input("Enter target language: ").strip()
                    await client.send_staff_response(text, lang)

                elif cmd == "4":
                    await client.end_session()
                    break

                elif cmd == "q":
                    break

                else:
                    print("Unknown command")

                await asyncio.sleep(0.5)

            except KeyboardInterrupt:
                break

    finally:
        await client.close()


async def main():
    parser = argparse.ArgumentParser(description="Test VaaNI Gateway")
    parser.add_argument("--scenario", type=int, choices=[1, 2], help="Run specific test scenario")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--url", default="ws://localhost:8000", help="Gateway WebSocket URL")

    args = parser.parse_args()

    if args.interactive:
        await test_interactive()
    elif args.scenario == 1:
        await test_scenario_1()
    elif args.scenario == 2:
        await test_scenario_2()
    else:
        print("Running all scenarios...\n")
        await test_scenario_1()
        await asyncio.sleep(2)
        await test_scenario_2()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted")
