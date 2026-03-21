# VaaNI Frontend

React + TypeScript + Vite frontend for the VaaNI multilingual banking branch assistant.

## Features

- 🎤 Real-time audio recording and streaming
- 🌐 Multi-language support with 15+ Indian languages
- 💬 Chat-style transcript with original + translated text
- 🤖 AI-powered response suggestions
- 📋 Step-by-step process guides for banking operations
- 🔊 TTS audio playback with waveform visualization
- 📊 Connection status and latency monitoring
- 🎨 Clean, professional UI for bank branch staff

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TailwindCSS** - Styling
- **Lucide React** - Icons

## Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The app will be available at `http://localhost:5173`

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Mock mode for development without backend
VITE_MOCK_MODE=false
```

## Development

### Mock Mode

For frontend development without the backend services:

```bash
# Create .env file
echo "VITE_MOCK_MODE=true" > .env

# Start dev server
npm run dev
```

Mock mode simulates WebSocket messages and allows you to test the UI independently.

### Connecting to Backend

Ensure the gateway service is running on `http://localhost:8000`:

```bash
# From the project root
docker-compose up gateway

# Or run gateway directly
cd gateway
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Then start the frontend with `VITE_MOCK_MODE=false` (or unset the env var).

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── TopBar.tsx      # Navigation and controls
│   ├── TranscriptPanel.tsx  # Conversation display
│   ├── SuggestionPanel.tsx  # AI suggestions
│   ├── ProcessGuide.tsx     # Banking process checklists
│   ├── ResponseComposer.tsx # Text input for staff
│   └── StatusBar.tsx    # Connection status bar
├── hooks/              # Custom React hooks
│   ├── useWebSocket.ts    # WebSocket connection management
│   ├── useMicrophone.ts   # Audio recording
│   └── useAudioPlayer.ts  # TTS playback
├── pages/              # Page components
│   ├── Session.tsx     # Main session page
│   └── Summary.tsx     # Post-session summary
├── types.ts            # TypeScript types
├── App.tsx             # Main app component
└── main.tsx            # Entry point
```

## Components

### TopBar
- Language selector with script previews
- Session timer
- Record/Pause button with flashing indicator
- New session button
- Connection status

### TranscriptPanel
- Dual-language chat bubbles
- Customer messages (blue, left) show original + translation
- Staff messages (gray, right)
- Auto-scroll to latest
- Confidence scores

### SuggestionPanel
- 2-3 AI-suggested responses
- Click to populate ResponseComposer
- Escalation warnings
- Loading states

### ProcessGuide
- Numbered step checklist
- Active step highlighting
- Manual completion toggle
- Progress bar

### ResponseComposer
- Free-form text input
- Auto-populate from suggestions
- Character counter
- Send button

### StatusBar
- Connection status
- Latency display
- Language confidence badge
- Session state

## Hooks

### useWebSocket
- Auto-reconnection with exponential backoff
- Message queuing while disconnected
- Typed send/receive API
- Connection status tracking

### useMicrophone
- MediaRecorder API integration
- 200ms audio chunking
- Base64 encoding
- Volume monitoring
- Pause/resume support

### useAudioPlayer
- Web Audio API playback
- Base64 audio decoding
- Waveform visualization
- Volume control

## WebSocket Protocol

### Client → Server
```json
// Audio chunk
{"type": "audio_chunk", "data": "base64..."}

// Language selection
{"type": "language_select", "language": "hi"}

// Staff response
{"type": "staff_response", "text": "...", "language": "hi"}

// End session
{"type": "session_end"}
```

### Server → Client
```json
// Transcript
{"type": "transcript", "text": "...", "language": "hi", "confidence": 0.92}

// Translation
{"type": "translation", "text": "...", "language": "en"}

// Suggestions
{"type": "suggestion", "suggestions": ["..."], "process_steps": [...], "escalate": false}

// TTS Audio
{"type": "tts_audio", "audio_b64": "...", "language": "hi"}

// Language detection
{"type": "lid_result", "language": "hi", "confidence": 0.95}

// Error
{"type": "error", "message": "..."}
```

## Browser Support

- Chrome 90+ (recommended for bank branch PCs)
- Edge 90+
- Firefox 88+
- Safari 14+

## Performance

- Lazy loading for page components
- Virtual scrolling for long transcripts (future)
- Optimized re-renders with React.memo
- Efficient audio chunking

## Accessibility

- ARIA labels on interactive elements
- Keyboard navigation support
- Focus indicators
- Screen reader friendly

## Troubleshooting

### WebSocket connection fails
- Ensure gateway service is running on port 8000
- Check browser console for CORS errors
- Verify ALLOWED_ORIGINS in gateway config

### Microphone not working
- Check browser permissions
- Ensure HTTPS or localhost
- Try a different browser (Chrome recommended)

### TTS not playing
- Check browser console for Web Audio API errors
- Verify audio format from gateway
- Check system volume

## License

MIT
