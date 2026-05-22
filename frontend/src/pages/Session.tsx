/**
 * Session Page
 *
 * Main layout for active customer session:
 * - TopBar: Full-width at top
 * - PipelineVisualization: Shows AI processing steps (mock mode)
 * - Main content: 60% left (TranscriptPanel + TextInput) | 40% right (SuggestionPanel + ProcessGuide)
 * - StatusBar: Bottom
 *
 * In mock mode: Text input is primary, mock pipeline processes everything client-side
 * In live mode: Microphone/WebSocket as before
 */

import { useState, useEffect, useCallback } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { useMicrophone } from '../hooks/useMicrophone';
import { useAudioPlayer } from '../hooks/useAudioPlayer';
import { useMockPipeline } from '../hooks/useMockPipeline';
import { TopBar } from '../components/TopBar';
import { TranscriptPanel } from '../components/TranscriptPanel';
import { SuggestionPanel } from '../components/SuggestionPanel';
import { ProcessGuide } from '../components/ProcessGuide';
import { ResponseComposer } from '../components/ResponseComposer';
import { StatusBar } from '../components/StatusBar';
import { TextInput } from '../components/TextInput';
import { PipelineVisualization, PipelineStepData } from '../components/PipelineVisualization';
import {
  TranscriptEntry,
  Suggestion,
  ProcessGuide as ProcessGuideType,
  BANKING_PROCESS_TEMPLATES,
  ClientMessage,
  SessionSummary,
} from '../types';

const MOCK_MODE = import.meta.env.VITE_MOCK_MODE === 'true';

interface SessionPageProps {
  sessionId: string;
  onSessionEnd?: (summary: any) => void;
  onShowMetrics?: () => void;
  demoPreload?: boolean;
}

export function SessionPage({ sessionId, onSessionEnd, onShowMetrics, demoPreload = false }: SessionPageProps) {
  // State
  const [selectedLanguage, setSelectedLanguage] = useState<string>('en');
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [processGuide, setProcessGuide] = useState<ProcessGuideType>(BANKING_PROCESS_TEMPLATES.general);
  const [languageConfidence, setLanguageConfidence] = useState<number | undefined>();
  const [pre_filledResponse, setPre_filledResponse] = useState<string>('');
  const [pipelineSteps, setPipelineSteps] = useState<PipelineStepData[]>([]);
  const [pipelineTotalTime, setPipelineTotalTime] = useState<number | undefined>();
  const [_sessionSummary, setSessionSummary] = useState<SessionSummary | null>(null);

  // Mock pipeline
  const mockPipeline = useMockPipeline();

  // WebSocket connection
  const { status, send, connect, disconnect } = useWebSocket({
    onMessage: handleServerMessage,
    onStatusChange: (newStatus) => {
      console.log('Connection status changed:', newStatus);
    },
  });

  // Microphone recording
  const { recordingState, startRecording, pauseRecording, resumeRecording } =
    useMicrophone({
      onChunk: handleAudioChunk,
      onError: (error) => console.error('Microphone error:', error),
    });

  // Audio player for TTS
  const { play, waveformData } = useAudioPlayer({
    autoPlay: true,
    onPlayEnd: () => console.log('Audio playback ended'),
  });

  // Connect to WebSocket on mount (or set mock mode as connected)
  useEffect(() => {
    connect(sessionId);
    return () => disconnect();
  }, [sessionId, connect, disconnect]);

  // Demo preload
  useEffect(() => {
    if (demoPreload && MOCK_MODE) {
      const timer = setTimeout(() => handleLoadDemo(), 500);
      return () => clearTimeout(timer);
    }
  }, [demoPreload]);

  // Send language selection when changed (non-mock mode)
  useEffect(() => {
    if (!MOCK_MODE && status.connected && selectedLanguage) {
      const message: ClientMessage = {
        type: 'language_select',
        language: selectedLanguage,
      };
      send(message);
    }
  }, [selectedLanguage, status.connected, send]);

  // Handle incoming WebSocket messages (non-mock mode)
  function handleServerMessage(message: any) {
    if (MOCK_MODE) return;

    console.log('Received message:', message);

    switch (message.type) {
      case 'transcript': {
        const newTranscriptEntry: TranscriptEntry = {
          id: `transcript-${Date.now()}`,
          role: 'customer',
          originalText: message.text,
          translatedText: undefined,
          language: message.language,
          timestamp: new Date(),
          confidence: message.confidence,
        };
        setTranscript((prev) => [...prev, newTranscriptEntry]);
        setLanguageConfidence(message.confidence);
        break;
      }

      case 'translation':
        setTranscript((prev) => {
          const updated = [...prev];
          const lastEntry = updated[updated.length - 1];
          if (lastEntry && lastEntry.role === 'customer') {
            lastEntry.translatedText = message.text;
          }
          return updated;
        });
        break;

      case 'suggestion': {
        const newSuggestions: Suggestion[] = message.suggestions.map((text: string, idx: number) => ({
          id: `suggestion-${idx}`,
          text,
          category: undefined,
        }));
        setSuggestions(newSuggestions);

        const detectedProcess = detectProcessFromSuggestions(message.suggestions, message.process_steps);
        if (detectedProcess) {
          setProcessGuide(detectedProcess);
        }
        break;
      }

      case 'tts_audio':
        play(message.audio_b64);
        break;

      case 'lid_result':
        setSelectedLanguage(message.language);
        setLanguageConfidence(message.confidence);
        break;

      case 'session_ended':
        console.log('Session ended:', message.session_id);
        onSessionEnd?.({ sessionId: message.session_id });
        break;

      case 'error':
        console.error('Server error:', message.message);
        break;

      default:
        console.warn('Unknown message type:', message);
    }
  }

  // Handle text input (mock mode primary input)
  const handleTextInput = useCallback(async (text: string) => {
    if (!MOCK_MODE) {
      handleSendResponse(text);
      return;
    }

    try {
      const result = await mockPipeline.processText(text);

      setPipelineSteps(result.pipelineSteps);
      setPipelineTotalTime(result.totalTime);
      setTranscript((prev) => [...prev, result.transcript]);
      setSelectedLanguage(result.transcript.language);
      setLanguageConfidence(result.transcript.confidence);
      setSuggestions(result.suggestions);
      setProcessGuide(result.processGuide);
    } catch (error) {
      console.error('Mock pipeline error:', error);
    }
  }, [mockPipeline]);

  // Handle audio chunk from microphone (non-mock mode)
  function handleAudioChunk(chunkBase64: string) {
    if (MOCK_MODE) return;
    const message: ClientMessage = {
      type: 'audio_chunk',
      data: chunkBase64,
    };
    send(message);
  }

  function detectProcessFromSuggestions(suggestions: string[], steps: string[]): ProcessGuideType | undefined {
    const text = suggestions.join(' ').toLowerCase() + ' ' + steps.join(' ').toLowerCase();

    if (text.includes('account') && text.includes('open')) return BANKING_PROCESS_TEMPLATES.account_opening;
    if (text.includes('loan') || text.includes('credit')) return BANKING_PROCESS_TEMPLATES.loan_inquiry;
    if (text.includes('card') || text.includes('debit') || text.includes('atm')) return BANKING_PROCESS_TEMPLATES.card_issue;
    if (text.includes('balance') || text.includes('statement')) return BANKING_PROCESS_TEMPLATES.balance_inquiry;
    if (text.includes('transfer') || text.includes('send') || text.includes('payment')) return BANKING_PROCESS_TEMPLATES.fund_transfer;
    if (text.includes('complaint') || text.includes('issue') || text.includes('problem')) return BANKING_PROCESS_TEMPLATES.complaint;
    return undefined;
  }

  const handleRecordToggle = () => {
    if (recordingState.isRecording) {
      if (recordingState.isPaused) { resumeRecording(); } else { pauseRecording(); }
    } else {
      startRecording();
    }
  };

  const handleSendResponse = useCallback(
    (text: string) => {
      if (!MOCK_MODE) {
        const message: ClientMessage = { type: 'staff_response', text, language: selectedLanguage };
        send(message);
      }
      const staffEntry: TranscriptEntry = {
        id: `staff-${Date.now()}`,
        role: 'staff',
        originalText: text,
        language: 'en',
        timestamp: new Date(),
      };
      setTranscript((prev) => [...prev, staffEntry]);
      setPre_filledResponse('');
    },
    [send, selectedLanguage]
  );

  const handleSuggestionClick = (suggestionText: string) => {
    setPre_filledResponse(suggestionText);
  };

  const handleStepToggle = (stepId: string) => {
    setProcessGuide((prev) => {
      if (!prev) return prev;
      const currentIdx = prev.steps.findIndex((s) => s.id === stepId);
      const currentStep = prev.steps[currentIdx];
      if (!currentStep || !currentStep.active) return prev;
      const newCompleted = !currentStep.completed;
      return {
        ...prev,
        steps: prev.steps.map((step, idx) => {
          if (step.id === stepId) return { ...step, completed: newCompleted };
          if (idx === currentIdx + 1 && newCompleted) return { ...step, active: true };
          return step;
        }),
      };
    });
  };

  const handleLoadDemo = useCallback(async () => {
    setTranscript([]);
    setSuggestions([]);
    setProcessGuide(BANKING_PROCESS_TEMPLATES.general);
    setPipelineSteps([]);
    const demoText = '\u092E\u0941\u091D\u0947 \u092B\u093F\u0915\u094D\u0938\u0921\u093C \u0921\u093F\u092A\u0949\u091C\u093F\u091F \u0916\u094B\u0932\u0928\u0940 \u0939\u0948, \u0915\u094D\u092F\u093E \u092C\u094D\u092F\u093E\u091C \u0926\u0930 \u092C\u0924\u093E\u090F\u0902\u0917\u0947?';
    await handleTextInput(demoText);
  }, [handleTextInput]);

  const handleEndSession = useCallback(() => {
    if (MOCK_MODE && transcript.length > 0) {
      const summaryData = mockPipeline.generateSummary(transcript);
      const summary: SessionSummary = { ...summaryData, transcript };
      setSessionSummary(summary);
      onSessionEnd?.(summary);
    } else {
      onSessionEnd?.({ sessionId });
    }
  }, [transcript, mockPipeline, onSessionEnd, sessionId]);

  const handleNewSession = () => { window.location.reload(); };

  return (
    <div className="h-screen flex flex-col bg-zinc-950">
      <TopBar
        selectedLanguage={selectedLanguage}
        onLanguageChange={setSelectedLanguage}
        isRecording={recordingState.isRecording}
        isPaused={recordingState.isPaused}
        onRecordToggle={handleRecordToggle}
        onNewSession={handleNewSession}
        onLoadDemo={MOCK_MODE ? handleLoadDemo : undefined}
        onShowMetrics={onShowMetrics}
        sessionDuration={recordingState.duration}
        isConnected={status.connected}
        isProcessing={mockPipeline.isProcessing}
      />

      {MOCK_MODE && pipelineSteps.length > 0 && (
        <PipelineVisualization steps={pipelineSteps} totalTime={pipelineTotalTime} />
      )}

      <div className="flex-1 flex overflow-hidden">
        <div className="w-3/5 flex flex-col border-r border-zinc-800">
          <div className="flex-1 overflow-hidden">
            <TranscriptPanel transcript={transcript} isPlaying={waveformData.length > 0} />
          </div>
          {MOCK_MODE ? (
            <TextInput
              onSubmit={handleTextInput}
              disabled={mockPipeline.isProcessing}
              placeholder="Type customer query in any Indian language..."
            />
          ) : (
            <ResponseComposer
              onSend={handleSendResponse}
              placeholder="Type your response here or click a suggestion..."
              disabled={!status.connected}
              prefillType={pre_filledResponse}
            />
          )}
        </div>

        <div className="w-2/5 flex flex-col">
          <div className="flex-1 overflow-hidden">
            <SuggestionPanel
              suggestions={suggestions}
              onSuggestionClick={handleSuggestionClick}
              escalate={false}
              loading={status.connected && suggestions.length === 0 && !MOCK_MODE}
            />
          </div>
          <div className="h-1/2 overflow-hidden">
            <ProcessGuide processGuide={processGuide} onStepToggle={handleStepToggle} />
          </div>
        </div>
      </div>

      <StatusBar
        connectionStatus={status}
        currentLanguage={selectedLanguage}
        languageConfidence={languageConfidence}
        sessionActive={status.connected}
        latency={status.latency}
      />

      {MOCK_MODE && transcript.length > 0 && (
        <div className="fixed bottom-16 right-6 z-10">
          <button
            onClick={handleEndSession}
            className="flex items-center gap-2 px-5 py-3 bg-red-600/80 hover:bg-red-500 text-white rounded-xl font-medium shadow-lg shadow-red-600/20 backdrop-blur transition-all"
          >
            End Session
          </button>
        </div>
      )}

      {recordingState.isRecording && !recordingState.isPaused && (
        <div className="fixed bottom-16 left-6 bg-zinc-900/90 text-zinc-100 px-4 py-2 rounded-lg shadow-xl shadow-black/30 backdrop-blur flex items-center gap-3 border border-zinc-800">
          <div className="flex gap-1 items-end h-6">
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="w-1 bg-banking-400 rounded"
                style={{ height: `${20 + recordingState.volume * 0.8}%`, transition: 'height 50ms ease' }}
              />
            ))}
          </div>
          <span className="text-sm font-medium">Recording...</span>
        </div>
      )}
    </div>
  );
}
