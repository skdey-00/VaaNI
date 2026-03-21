"""
FD (Fixed Deposit) Demo Scenario Runner.

A scripted end-to-end demo that:
1. Starts a session
2. Sends Hindi FD inquiry audio in chunks
3. Prints each WebSocket message with timing
4. Shows LLM suggestions and process steps
5. Sends staff response
6. Ends session and prints bilingual summary

Usage:
    python demo/scenario_fd.py
"""

import asyncio
import websockets
import requests
import json
import base64
import time
from pathlib import Path
from datetime import datetime


# Configuration
GATEWAY_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"
AUDIO_FILE = Path("demo/audio/hindi_fd_inquiry.wav")


class Colors:
    """Terminal color codes."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text:^70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")


def print_step(step_num: int, text: str):
    """Print a step header."""
    print(f"{Colors.OKCYAN}{Colors.BOLD}[Step {step_num}]{Colors.ENDC} {text}")


def print_message(msg_type: str, data: dict, elapsed: float):
    """Print a WebSocket message with timing."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

    type_colors = {
        "lid_result": Colors.OKBLUE,
        "transcript": Colors.OKGREEN,
        "translation": Colors.OKCYAN,
        "suggestion": Colors.WARNING,
        "tts_audio": Colors.HEADER,
        "error": Colors.FAIL,
    }

    color = type_colors.get(msg_type, Colors.ENDC)

    print(f"  {Colors.OKGREEN}[{timestamp}]{Colors.ENDC} "
          f"{color}{msg_type.upper()}{Colors.ENDC} "
          f"{Colors.BOLD}({elapsed:.2f}s){Colors.ENDC}")

    # Print relevant data based on message type
    if msg_type == "transcript":
        print(f"    📝 Text: {data.get('text', 'N/A')}")
        print(f"    🌐 Language: {data.get('language', 'N/A')} "
              f"| Confidence: {data.get('confidence', 0):.2f}")

    elif msg_type == "translation":
        print(f"    🌐 Translation: {data.get('text', 'N/A')}")

    elif msg_type == "suggestion":
        print(f"    💡 Suggestions:")
        for i, sugg in enumerate(data.get('suggestions', []), 1):
            print(f"       {i}. {sugg}")
        if data.get('escalate'):
            print(f"    ⚠️  ESCALATION RECOMMENDED")

    elif msg_type == "lid_result":
        print(f"    🔍 Detected: {data.get('language', 'N/A')} "
              f"| Confidence: {data.get('confidence', 0):.2f}")

    elif msg_type == "tts_audio":
        audio_len = len(data.get('audio_b64', ''))
        print(f"    🔊 TTS Audio: {audio_len} chars (base64)")

    elif msg_type == "error":
        print(f"    ❌ Error: {data.get('message', 'Unknown error')}")

    print()


def load_audio_file(file_path: Path) -> str:
    """Load audio file and return as base64."""
    if not file_path.exists():
        print(f"{Colors.WARNING}Warning: Audio file not found: {file_path}{Colors.ENDC}")
        print(f"{Colors.WARNING}Using mock audio data{Colors.ENDC}")
        # Return mock audio data
        return base64.b64encode(b"MOCK_AUDIO" * 1000).decode('utf-8')

    with open(file_path, 'rb') as f:
        audio_data = f.read()
        return base64.b64encode(audio_data).decode('utf-8')


async def run_fd_scenario():
    """Run the complete FD inquiry demo scenario."""

    print_header("VaaNI FD Demo Scenario")
    print(f"{Colors.BOLD}Scenario: Hindi customer inquires about opening a Fixed Deposit{Colors.ENDC}")
    print(f"{Colors.BOLD}Expected Flow: LID → Transcript → Translation → Suggestions → TTS{Colors.ENDC}\n")

    # Step 1: Start session
    print_step(1, "Creating new session...")
    response = requests.post(f"{GATEWAY_URL}/session/start")
    if response.status_code != 200:
        print(f"{Colors.FAIL}Failed to create session: {response.text}{Colors.ENDC}")
        return

    session_id = response.json()["session_id"]
    print(f"{Colors.OKGREEN}✅ Session created: {session_id}{Colors.ENDC}\n")

    # Step 2: Connect WebSocket
    print_step(2, f"Connecting to WebSocket: {WS_URL}/ws/{{session_id}}")
    ws_uri = f"{WS_URL}/ws/{session_id}"

    try:
        async with websockets.connect(ws_uri) as ws:
            print(f"{Colors.OKGREEN}✅ Connected{Colors.ENDC}\n")

            # Step 3: Select language
            print_step(3, "Selecting Hindi language...")
            await ws.send_json({
                "type": "language_select",
                "language": "hi"
            })
            print(f"{Colors.OKGREEN}✅ Language set to Hindi{Colors.ENDC}\n")

            # Step 4: Load and send audio
            print_step(4, "Sending FD inquiry audio in chunks...")

            audio_b64 = load_audio_file(AUDIO_FILE)

            # Send in chunks (simulate real-time streaming)
            chunk_size = len(audio_b64) // 5
            for i in range(5):
                chunk = audio_b64[i*chunk_size:(i+1)*chunk_size]
                await ws.send_json({
                    "type": "audio_chunk",
                    "data": chunk
                })
                await asyncio.sleep(0.3)  # Simulate real-time audio

            print(f"{Colors.OKGREEN}✅ Audio sent in 5 chunks{Colors.ENDC}\n")

            # Step 5: Receive and display messages
            print_step(5, "Receiving real-time messages...")
            print(f"{Colors.BOLD}{'─'*70}{Colors.ENDC}")

            start_time = time.time()
            message_count = 0
            expected_order = []

            while time.time() - start_time < 15:  # 15 second timeout
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    data = json.loads(message)
                    msg_type = data.get("type")
                    elapsed = time.time() - start_time

                    print_message(msg_type, data, elapsed)
                    expected_order.append(msg_type)
                    message_count += 1

                    # Stop after receiving suggestion
                    if msg_type == "suggestion":
                        break

                except asyncio.TimeoutError:
                    continue

            print(f"{Colors.BOLD}{'─'*70}{Colors.ENDC}\n")
            print(f"{Colors.OKGREEN}✅ Received {message_count} messages{Colors.ENDC}\n")

            # Step 6: Send staff response
            print_step(6, "Staff sends response...")
            await ws.send_json({
                "type": "staff_response",
                "text": "जरूर, आपका फिक्स्ड डिपॉजिट खाता 7.5% ब्याज दर पर खुल जाएगा। कृपया आधार कार्ड और पैन कार्ड लाएं।",
                "language": "hi"
            })
            print(f"{Colors.OKGREEN}✅ Response sent{Colors.ENDC}\n")

            # Step 7: Receive TTS
            print_step(7, "Receiving TTS audio...")
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(message)
                elapsed = time.time() - start_time
                print_message(data.get("type", "unknown"), data, elapsed)
            except asyncio.TimeoutError:
                print(f"{Colors.WARNING}⚠️  No TTS response (might be processing){Colors.ENDC}\n")

            # Step 8: End session
            print_step(8, "Ending session...")
            await ws.send_json({"type": "session_end"})

            try:
                message = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(message)
                if data.get("type") == "session_ended":
                    print(f"{Colors.OKGREEN}✅ Session ended{Colors.ENDC}\n")
            except asyncio.TimeoutError:
                print(f"{Colors.WARNING}⚠️  No session end confirmation{Colors.ENDC}\n")

    except websockets.exceptions.InvalidHandshake:
        print(f"{Colors.FAIL}❌ Failed to connect to WebSocket{Colors.ENDC}")
        print(f"{Colors.FAIL}   Make sure the gateway is running on port 8000{Colors.ENDC}")
        return

    except Exception as e:
        print(f"{Colors.FAIL}❌ Error: {e}{Colors.ENDC}")
        return

    # Step 9: Get summary
    print_step(9, "Fetching bilingual summary...")
    response = requests.post(f"{GATEWAY_URL}/session/{session_id}/end")
    if response.status_code == 200:
        summary = response.json()
        print(f"{Colors.OKGREEN}✅ Summary generated{Colors.ENDC}\n")

        print(f"{Colors.BOLD}📝 English Summary:{Colors.ENDC}")
        print(f"   {summary.get('summary_en', 'N/A')}\n")

        print(f"{Colors.BOLD}📝 Hindi Summary:{Colors.ENDC}")
        print(f"   {summary.get('summary_lang', 'N/A')}\n")

        print(f"{Colors.BOLD}🏷️  Query Type:{Colors.ENDC} {summary.get('query_type', 'N/A')}\n")
    else:
        print(f"{Colors.FAIL}❌ Failed to get summary{Colors.ENDC}\n")

    # Step 10: Export PDF
    print_step(10, "Exporting PDF summary...")
    response = requests.get(f"{GATEWAY_URL}/session/{session_id}/export/pdf")
    if response.status_code == 200:
        filename = f"fd_demo_{session_id[:8]}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"{Colors.OKGREEN}✅ PDF exported: {filename}{Colors.ENDC}\n")
    else:
        print(f"{Colors.FAIL}❌ Failed to export PDF{Colors.ENDC}\n")

    print_header("Demo Complete!")
    print(f"{Colors.OKGREEN}{Colors.BOLD}All steps completed successfully!{Colors.ENDC}\n")


def main():
    """Main entry point."""
    try:
        asyncio.run(run_fd_scenario())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Demo interrupted{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Demo failed: {e}{Colors.ENDC}")


if __name__ == "__main__":
    main()
