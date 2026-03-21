# Demo Scripts

Scripts and audio files for demonstrating VaaNI capabilities.

## Scripts

### seed_audio.py
Generate synthetic test audio files using TTS (Text-to-Speech).

**Usage:**
```bash
# Using Google TTS (requires internet)
python demo/seed_audio.py

# Output: demo/audio/
#   - hindi_fd_inquiry.wav
#   - tamil_loan_inquiry.wav
#   - bengali_account_opening.wav
#   - english_balance_inquiry.wav
#   - spanish_card_inquiry.wav
```

**Requirements:**
```bash
pip install gtts pyttsx3
```

**Audio Files Generated:**

| File | Language | Script | Purpose |
|------|----------|--------|---------|
| `hindi_fd_inquiry.wav` | Hindi | हिंदी | Customer asks about FD opening |
| `tamil_loan_inquiry.wav` | Tamil | தமிழ் | Customer asks about loan |
| `bengali_account_opening.wav` | Bengali | বাংলা | Customer wants to open account |
| `english_balance_inquiry.wav` | English | English | Customer checks balance |
| `spanish_card_inquiry.wav` | Spanish | Español | Customer asks for debit card |

### scenario_fd.py
Run a scripted Fixed Deposit demo scenario.

**Usage:**
```bash
# Ensure services are running
docker-compose up -d

# Run demo
python demo/scenario_fd.py
```

**What It Does:**
1. Creates a new session
2. Connects via WebSocket
3. Selects Hindi language
4. Sends Hindi FD inquiry audio in chunks
5. Displays real-time messages (LID → Transcript → Translation → Suggestions)
6. Sends staff response in Hindi
7. Receives TTS audio
8. Ends session
9. Fetches and displays bilingual summary
10. Exports PDF

**Expected Output:**
```
======================================================================
                    VaaNI FD Demo Scenario
======================================================================

Scenario: Hindi customer inquires about opening a Fixed Deposit
Expected Flow: LID → Transcript → Translation → Suggestions → TTS

[Step 1] Creating new session...
✅ Session created: abc-123-def

[Step 2] Connecting to WebSocket...
✅ Connected

[Step 3] Selecting Hindi language...
✅ Language set to Hindi

[Step 4] Sending FD inquiry audio in chunks...
✅ Audio sent in 5 chunks

[Step 5] Receiving real-time messages...
──────────────────────────────────────────────────────────────────────
  [10:30:15.123] LID_RESULT (0.45s)
    🔍 Detected: hi | Confidence: 0.95

  [10:30:15.567] TRANSCRIPT (1.23s)
    📝 Text: मैं एक फिक्स्ड डिपॉजिट खाता खोलना चाहता हूं
    🌐 Language: hi | Confidence: 0.92

  [10:30:15.890] TRANSLATION (2.12s)
    🌐 Translation: I want to open a fixed deposit account

  [10:30:16.234] SUGGESTION (3.45s)
    💡 Suggestions:
       1. I can help you open an FD account with 7.5% interest rate
       2. Would you like to know about our FD schemes?
       3. Please bring your Aadhaar and PAN card
──────────────────────────────────────────────────────────────────────
✅ Received 4 messages

[Step 6] Staff sends response...
✅ Response sent

[Step 7] Receiving TTS audio...
  [10:30:18.456] TTS_AUDIO (5.67s)
    🔊 TTS Audio: 45678 chars (base64)

[Step 8] Ending session...
✅ Session ended

[Step 9] Fetching bilingual summary...
✅ Summary generated

📝 English Summary:
   Customer inquired about opening a Fixed Deposit account...

📝 Hindi Summary:
   ग्राहक ने फिक्स्ड डिपॉजिट खाता खोलने के बारे में पूछा...

🏷️  Query Type: FD Inquiry

[Step 10] Exporting PDF...
✅ PDF exported: fd_demo_abc123de.pdf

======================================================================
                        Demo Complete!
======================================================================
```

## Custom Scenarios

Create your own demo scenarios by modifying `scenario_fd.py`:

```python
# Change audio file
AUDIO_FILE = Path("demo/audio/tamil_loan_inquiry.wav")

# Change language
await ws.send_json({"type": "language_select", "language": "ta"})

# Change staff response
await ws.send_json({
    "type": "staff_response",
    "text": "கல்வி கடன் பெற சம்பள படிவம் மற்றும் ஆதார் அட்டை தேவை",
    "language": "ta"
})
```

## Troubleshooting

### Audio Not Playing
- Check audio file exists: `ls demo/audio/`
- Verify format: `file demo/audio/hindi_fd_inquiry.wav`

### WebSocket Connection Failed
- Ensure gateway is running: `curl http://localhost:8000/health`
- Check firewall settings

### No Messages Received
- Check mock mode: Set `MOCK_MODE=false` in `.env`
- Verify services are healthy: `docker-compose ps`

## Demo for Judges

Follow `DEMO_SCRIPT.md` for a structured 3-minute hackathon presentation.
